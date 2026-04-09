import glob
import os
import re
import json
import time
import subprocess
import requests
import shutil
import base64
from pathlib import Path
from pytrends.request import TrendReq

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


# =========================
# ENV
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
HF_TOKEN = os.getenv("HF_TOKEN")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY = os.getenv("KAGGLE_KEY")

YT_CHANNEL_ID = os.getenv("YT_CHANNEL_ID")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

VIDEOS_PER_DAY = 2

MAX_SCRIPT_REWRITES = 2
KAGGLE_TIMEOUT = 1800

FALLBACK_TOPICS = [
    "The AI discovery experts say could change daily life",
    "The hidden science behind human decision making"
]

PLACEHOLDER_THUMBNAIL_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7XxkQAAAAASUVORK5CYII="
)


# =========================
# UTIL
# =========================

def safe_json(text):
    try:
        return json.loads(text)
    except:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])


def retry_request(func, attempts=3, context="request", fallback=None, raise_on_failure=False):

    for i in range(attempts):

        try:
            return func()

        except Exception as e:

            msg = str(e)
            if "RATE_LIMIT" in msg:
                wait = 10 + i * 5
            else:
                wait = min(10, 3 + i * 2)

            print(f"[{context}] attempt {i + 1}/{attempts} failed: {e}")

            if i < attempts - 1:
                time.sleep(wait)

    print(f"[{context}] max retries reached. Using fallback.")

    if raise_on_failure:
        raise Exception(f"Max retries reached for {context}")

    return fallback


def safe_api_json(r):

    try:
        data = r.json()
    except:
        raise Exception("API returned invalid JSON")

    # If Groq returned an error
    if "error" in data:

        msg = data["error"]["message"]

        # Handle rate limit
        if "rate limit" in msg.lower() or "tokens per minute" in msg.lower():
            print("Groq rate limit hit. Waiting 5 seconds...")
            time.sleep(5)
            raise Exception("RATE_LIMIT")

        raise Exception(f"Groq API error: {msg}")

    if "choices" not in data:
        raise Exception(f"Malformed API response: {data}")

    return data


# =========================
# GROQ HELPER
# =========================

def groq_chat(prompt, model=GROQ_MODEL):

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages":[{"role":"user","content":prompt}]
        },
        timeout=120
    )

    data = safe_api_json(r)

    # throttle to avoid Groq TPM limits
    time.sleep(12)

    return data


# =========================
# THUMBNAIL PROMPT
# =========================

def generate_thumbnail_prompt(title):

    def call():

        prompt = f"""
Create a HIGH-CTR YouTube thumbnail concept.

Video title:
{title}

Your task is to design a thumbnail concept that maximizes curiosity and emotional tension so viewers cannot resist clicking.

Design principles:

- one dominant subject
- extreme emotional expression
- visual tension or danger
- strong contrast
- dramatic lighting
- cinematic realism
- mysterious element that raises a question

Thumbnail psychology rules:

Use visual storytelling similar to viral thumbnails:
• suspense
• danger
• shock
• discovery
• impossible scale
• unexpected comparison

Return ONLY a short visual description suitable for image generation.
"""

        data = groq_chat(prompt)
        
        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")

        return data["choices"][0]["message"]["content"]

    return retry_request(call, context="thumbnail-prompt", fallback="cinematic dramatic documentary scene, high contrast, mysterious lighting")


def ensure_artifacts_dir():
    Path("artifacts").mkdir(exist_ok=True)


def create_placeholder_thumbnail(reason="unknown"):
    ensure_artifacts_dir()
    path = "artifacts/thumbnail.png"
    with open(path, "wb") as f:
        f.write(base64.b64decode(PLACEHOLDER_THUMBNAIL_B64))
    print(f"Using placeholder thumbnail due to: {reason}")
    return path


# =========================
# THUMBNAIL IMAGE
# =========================

def generate_thumbnail(prompt):

    def call():

        api = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        if not HF_TOKEN:
            raise Exception("HF_TOKEN is not configured")

        r = requests.post(
            api,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )

        if r.status_code != 200:
            raise Exception(f"HuggingFace image error: {r.status_code} {r.text[:300]}")

        ensure_artifacts_dir()

        path = "artifacts/thumbnail.png"

        with open(path, "wb") as f:
            f.write(r.content)

        return path

    result = retry_request(call, attempts=2, context="huggingface-thumbnail", fallback=None)
    if result:
        return result
    return create_placeholder_thumbnail("huggingface generation failure")



def generate_best_topics(seeds):

    def call():

        prompt = f"""
You are selecting the best viral YouTube topics.

Goal:
Pick topics capable of reaching 1M+ views.

Rules:

Topics must include:
- mystery
- shocking discovery
- hidden truth
- dangerous technology
- unexplained phenomenon
- scientific breakthrough
- future implications

Seeds:
{seeds}

Generate the TOP 10 most viral YouTube video topics.

Return ONLY a numbered list.

Example format:

1. topic
2. topic
3. topic
"""

        data = groq_chat(prompt)

        return data["choices"][0]["message"]["content"]

    text = retry_request(call)

    lines = text.split("\n")

    topics = []

    for line in lines:

        m = re.match(r"^\d+[\.\)]\s*(.+)", line)

        if m:
            topics.append(m.group(1).strip())

    return topics
# =========================
# VIRAL ANGLE GENERATOR
# =========================

def generate_angles(topics):

    def call():

        prompt = f"""
For each topic generate 3 viral YouTube story angles.

Goal:
maximize curiosity, controversy and storytelling potential.

Angles must trigger psychological tension such as:

- hidden truth
- forbidden knowledge
- shocking discovery
- impossible technology
- danger
- mystery
- global consequences

Topics:
{topics}

Return list only.
"""

        data = groq_chat(prompt)
        
        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")

        angles = data["choices"][0]["message"]["content"].split("\n")

        return [x.strip("- ").strip() for x in angles if x]

    return retry_request(call)


# =========================
# TOPIC NARRATIVE FILTER
# =========================

def filter_storyworthy_topics(topics):

    def call():

        prompt = f"""
You are selecting topics for viral YouTube storytelling.

Only keep topics that contain strong narrative potential.

A topic is good if it contains elements like:

- secret
- hidden discovery
- shocking experiment
- forbidden research
- dangerous technology
- mysterious phenomenon
- scientists shocked
- government hiding something
- unexpected consequences
- something that changes what we thought was true

Topics:
{topics}

Return ONLY the topics that have strong story tension.

Return one topic per line.
"""

        data = groq_chat(prompt)

        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")

        lines = data["choices"][0]["message"]["content"].split("\n")

        return [x.strip("- ").strip() for x in lines if x]

    return retry_request(call)

# =========================
# TOPIC DISCOVERY
# =========================

def rank_topics(angles):

    prompt = f"""
Rank these YouTube topics for viral potential.

Consider:

- curiosity
- controversy
- global interest
- story potential
- future impact
- emotional tension
- shock factor

Topics:
{angles}

IMPORTANT RULES:

Return ONLY a numbered list.

Example format:

1. topic one
2. topic two
3. topic three
4. topic four
5. topic five

Do NOT include explanations.
Do NOT include commentary.
Do NOT include markdown formatting.
Do NOT include quotes.
Return only the numbered list.
"""

    def call():
        return groq_chat(prompt)

    ranked_text = retry_request(call)["choices"][0]["message"]["content"]

    lines = ranked_text.split("\n")

    ranked = []

    for line in lines:

        line = line.strip()

        m = re.match(r"^\d+[\.\)]\s*(.+)", line)

        if m:
            topic = m.group(1).strip()

            if len(topic) > 10:
                ranked.append(topic)

    return ranked

def discover_trending_topics():

    google_trends = []
    youtube_trends = []
    news_topics = []

    # ---------------------------
    # GOOGLE TRENDS
    # ---------------------------

    try:

        pytrend = TrendReq(
            hl="en-US",
            tz=360
        )

        google = pytrend.trending_searches(pn="united_states")

        google_trends = google[0].tolist()[:15]

        print("Google trends:", google_trends)

    except Exception as e:

        print("Google Trends failed:", e)

    # ---------------------------
    # YOUTUBE TRENDING
    # ---------------------------

    try:

        youtube = youtube_client()

        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="US",
            maxResults=25
        )

        response = request.execute()

        youtube_trends = [
            v["snippet"]["title"]
            for v in response.get("items", [])
        ]

        print("YouTube trends:", youtube_trends[:10])

    except Exception as e:

        print("YouTube API failed:", e)

    # ---------------------------
    # NEWS API
    # ---------------------------

    try:

        news_url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=20&apiKey={NEWS_API_KEY}"

        news = requests.get(news_url, timeout=30).json()

        news_topics = [
            re.split(r"[-|:]", a["title"])[0].strip()
            for a in news.get("articles", [])
        ]

        print("News topics:", news_topics[:10])

    except Exception as e:

        print("News API failed:", e)

    # ---------------------------
    # MERGE SEEDS
    # ---------------------------

    seeds = list(set(google_trends + youtube_trends + news_topics))

    # ---------------------------
    # HARD FALLBACK SEEDS
    # ---------------------------

    if len(seeds) == 0:

        seeds = [

                # -----------------------
                # MONEY / WEALTH / FINANCIAL FREEDOM
                # -----------------------

                "The wealth strategy experienced investors quietly use before major market shifts",
                "The financial mistake millions make that slowly destroys long-term wealth",
                "The hidden investing pattern experts notice before economic booms",
                "The money rule wealthy individuals follow during financial crises",
                "The surprising financial behavior that quietly builds massive wealth",
                "The investment strategy professionals use when markets become unstable",
                "The little-known wealth protection method used during economic uncertainty",
                "The financial habit that silently separates wealthy people from everyone else",
                "The surprising economic signal investors watch before major opportunities",
                "The financial principle that helped some investors grow fortunes over time",


                # -----------------------
                # HEALTH / LONGEVITY / HUMAN BODY
                # -----------------------

                "The daily habit researchers link to dramatically longer lifespans",
                "The surprising health pattern scientists discovered among people living past 100",
                "The silent health mistake doctors say many people repeat for years",
                "The hidden biological process scientists believe may control aging",
                "The sleep discovery researchers say could change long-term health",
                "The unexpected lifestyle factor scientists associate with longevity",
                "The surprising health signal doctors notice before serious problems appear",
                "The unusual habit researchers discovered while studying long-lived populations",
                "The biological mechanism scientists believe influences how humans age",
                "The simple health behavior linked to improved long-term wellbeing",


                # -----------------------
                # PSYCHOLOGY / HUMAN BEHAVIOR / INFLUENCE
                # -----------------------

                "The psychological pattern that quietly influences most human decisions",
                "The subtle behavior that dramatically changes how people perceive you",
                "The communication technique psychologists say increases persuasion",
                "The surprising mental bias that shapes everyday decision making",
                "The behavioral signal experts associate with strong leadership",
                "The psychological trigger that can change how people respond to ideas",
                "The subtle communication mistake that weakens influence",
                "The conversation habit highly persuasive people use instinctively",
                "The human behavior pattern psychologists observe during high pressure situations",
                "The mental shortcut the brain uses when making complex decisions",


                # -----------------------
                # SUCCESS / PRODUCTIVITY / HIGH PERFORMANCE
                # -----------------------

                "The daily discipline habit shared by highly successful individuals",
                "The productivity system some high performers quietly rely on",
                "The mental model exceptional problem-solvers frequently use",
                "The focus strategy experts use to maintain extreme productivity",
                "The surprising routine researchers associate with high achievement",
                "The decision habit that quietly improves long-term success",
                "The productivity mistake that silently reduces performance",
                "The cognitive strategy that helps people make better decisions",
                "The simple habit that increases long-term discipline",
                "The performance mindset researchers observe in high achievers",


                # -----------------------
                # STUDY / LEARNING / EXAM PERFORMANCE
                # -----------------------

                "The learning technique researchers say dramatically improves memory retention",
                "The study strategy high-performing students often rely on",
                "The cognitive trick that helps information stay longer in memory",
                "The revision pattern educators associate with exam success",
                "The surprising study habit researchers link to faster learning",
                "The mental strategy students use during high-pressure exams",
                "The learning shortcut scientists discovered in neuroscience research",
                "The focus technique that helps students absorb information faster",
                "The cognitive habit linked to stronger academic performance",
                "The study mistake that quietly weakens memory recall",


                # -----------------------
                # TECHNOLOGY / AI / FUTURE
                # -----------------------

                "The artificial intelligence behavior researchers did not expect to observe",
                "The technology breakthrough scientists believe could reshape industries",
                "The unexpected capability researchers discovered in advanced AI systems",
                "The computing discovery that surprised technology experts",
                "The technological development researchers believe could transform society",
                "The innovation scientists say may redefine human capability",
                "The AI experiment that produced results nobody predicted",
                "The emerging technology experts believe could change daily life",
                "The discovery in computing power that stunned researchers",
                "The technological shift researchers believe could shape the next decade",


                # -----------------------
                # SCIENCE / MYSTERY / UNKNOWN DISCOVERIES
                # -----------------------

                "The mysterious signal scientists detected while studying deep space",
                "The scientific anomaly researchers discovered during a major experiment",
                "The discovery that forced scientists to reconsider existing theories",
                "The strange phenomenon researchers observed that remains unexplained",
                "The unexpected observation scientists are still trying to understand",
                "The discovery researchers believe could change how we understand reality",
                "The unexplained anomaly detected using modern scientific instruments",
                "The phenomenon scientists continue investigating years later",
                "The unusual discovery researchers made during advanced experiments",
                "The scientific mystery experts are still trying to solve",


                # -----------------------
                # SURVIVAL / RISK / EXTREME HUMAN CONDITIONS
                # -----------------------

                "The survival behavior experts observe during extreme danger",
                "The mental response humans experience in life-threatening situations",
                "The survival skill experts say increases chances in disasters",
                "The psychological reaction researchers observe during crises",
                "The surprising factor that determines survival in emergencies",
                "The behavior pattern experts notice under extreme pressure",
                "The mental strategy used by people who survive extreme conditions",
                "The resilience trait researchers associate with survival",
                "The unexpected decision pattern humans show during danger",
                "The survival instinct scientists continue studying",

                # -----------------------
                # MONEY / WEALTH / FINANCIAL ADVANTAGE
                # -----------------------

                "The financial habit that quietly builds wealth while most people overlook it",
                "The investing principle wealthy individuals rely on during uncertain markets",
                "The money mistake that slowly erodes wealth for millions of people",
                "The financial signal experienced investors watch before major opportunities",
                "The wealth protection strategy some investors use during economic instability",
                "The simple money rule that quietly compounds wealth over time",
                "The financial behavior that separates long-term investors from short-term gamblers",
                "The investing mindset that helped ordinary people build extraordinary wealth",
                "The financial pattern experts notice before markets dramatically shift",
                "The wealth building strategy that could change how people think about money",


                # -----------------------
                # HEALTH / LONGEVITY / PERSONAL WELLBEING
                # -----------------------

                "The daily habit researchers link to dramatically longer and healthier lives",
                "The surprising lifestyle pattern scientists discovered among people living past 100",
                "The silent health mistake doctors say many people unknowingly repeat",
                "The sleep behavior researchers believe strongly influences long-term health",
                "The biological process scientists are studying to better understand aging",
                "The simple habit researchers associate with improved long-term health",
                "The unexpected health signal doctors sometimes notice before serious illness",
                "The longevity pattern scientists discovered while studying centenarians",
                "The lifestyle factor researchers believe influences how humans age",
                "The health routine that could quietly improve long-term wellbeing",


                # -----------------------
                # PSYCHOLOGY / INFLUENCE / SOCIAL ADVANTAGE
                # -----------------------

                "The psychological habit that quietly increases influence in conversations",
                "The subtle behavior that changes how people perceive confidence",
                "The persuasion technique psychologists say improves communication impact",
                "The surprising mental bias that influences everyday decisions",
                "The communication mistake that weakens influence without people realizing it",
                "The psychological pattern experts say shapes many human interactions",
                "The conversation habit highly persuasive people naturally use",
                "The subtle signal that makes people appear more trustworthy",
                "The mental shortcut the brain uses when making complex decisions",
                "The behavioral insight psychologists say improves social awareness",


                # -----------------------
                # SUCCESS / PRODUCTIVITY / PERSONAL PERFORMANCE
                # -----------------------

                "The discipline habit many high performers quietly practice every day",
                "The productivity system some successful individuals rely on for focus",
                "The mental model exceptional problem-solvers frequently use",
                "The focus strategy researchers say improves long-term productivity",
                "The daily routine researchers associate with sustained success",
                "The productivity mistake that slowly reduces long-term performance",
                "The mindset pattern observed in highly disciplined individuals",
                "The cognitive habit linked to better decision making",
                "The simple change that can dramatically improve daily productivity",
                "The performance principle many successful people follow consistently",


                # -----------------------
                # STUDY / LEARNING / EXAM SUCCESS
                # -----------------------

                "The learning technique researchers say dramatically improves memory retention",
                "The study strategy top students rely on during high-pressure exams",
                "The cognitive trick that helps information stay longer in memory",
                "The revision habit associated with stronger exam performance",
                "The learning shortcut researchers discovered in neuroscience",
                "The focus technique that helps students absorb information faster",
                "The memory strategy that improves recall during stressful exams",
                "The study mistake that weakens learning efficiency",
                "The learning pattern educators associate with academic success",
                "The mental framework that helps people understand complex topics faster",


                # -----------------------
                # TECHNOLOGY / AI / FUTURE ADVANTAGE
                # -----------------------

                "The artificial intelligence capability researchers did not expect to observe",
                "The technology development experts believe could change everyday life",
                "The computing discovery that surprised many technology researchers",
                "The emerging technology scientists believe may reshape industries",
                "The AI experiment that produced results nobody predicted",
                "The technological shift researchers believe will shape the next decade",
                "The innovation scientists say may redefine human capability",
                "The computing breakthrough researchers are closely watching",
                "The new technology researchers believe could transform productivity",
                "The discovery in artificial intelligence that surprised its creators",


                # -----------------------
                # SCIENCE / DISCOVERY / HIDDEN KNOWLEDGE
                # -----------------------

                "The mysterious signal scientists detected while studying deep space",
                "The scientific anomaly researchers discovered during a major experiment",
                "The discovery that forced scientists to rethink existing theories",
                "The strange phenomenon researchers observed that remains unexplained",
                "The unexpected observation scientists are still trying to understand",
                "The discovery researchers believe could change our understanding of reality",
                "The unexplained anomaly detected using modern scientific instruments",
                "The phenomenon scientists continue investigating years later",
                "The unusual discovery researchers made during advanced experiments",
                "The scientific mystery experts are still trying to solve",


                # -----------------------
                # SURVIVAL / RISK / HUMAN LIMITS
                # -----------------------

                "The survival habit experts say increases chances during emergencies",
                "The psychological response humans experience in life-threatening situations",
                "The survival skill that dramatically improves chances in dangerous conditions",
                "The surprising factor experts say influences survival during disasters",
                "The behavior pattern researchers observe under extreme pressure",
                "The mental strategy used by people who survive extreme situations",
                "The resilience trait experts associate with long-term survival",
                "The decision pattern humans follow during crisis situations",
                "The survival instinct scientists continue studying today",
                "The unexpected behavior humans display in extreme danger"
                ]

    seeds = seeds[:20]

    print("Seed topics:", seeds)

    # ---------------------------
    # GROQ VIRAL TOPIC GENERATION
    # ---------------------------

    def generate_topics():

        prompt = f"""
You are selecting the most viral YouTube documentary topics.

Goal:
Find topics capable of getting millions of views.

Rules:

Topics must include at least one of these elements:

- shocking scientific discovery
- dangerous experiment
- hidden technology
- mysterious signal
- unexplained cosmic event
- secret research
- future technology risk
- unexpected discovery

Seeds:
{seeds}

Generate the TOP 10 most viral YouTube video topics.

Return ONLY a numbered list.

Example:

1. topic
2. topic
3. topic
"""

        return groq_chat(prompt)

    text = retry_request(generate_topics)["choices"][0]["message"]["content"]

    lines = text.split("\n")

    topics = []

    for line in lines:

        m = re.match(r"^\d+[\.\)]\s*(.+)", line)

        if m:
            topics.append(m.group(1).strip())

    print("Generated topics:", topics)

    if not topics:
        topics = FALLBACK_TOPICS

    return topics[:VIDEOS_PER_DAY]    


# =========================
# SCRIPT OUTLINE
# =========================

def generate_outline(topic):

    def call():

        prompt = f"""
Create a super interesting, high-retention YouTube outline. 
Your efffort must be such that people can not leave the video in mid way.
Generate curiosity which is most important. Curiosity should reflect all across the video.
Listen, I am not making a joke with you. So be very very serious first. This must not be a toy. 
The outline must be top class in the world, and no compromise on that. This is the haard rule, lock it first.

Length: 8-10 minute video.

Structure:

STRUCTURE RULE (MANDATORY):

The outline MUST follow this curiosity architecture:

1. HOOK (first 10 seconds)
   - shocking statement or mystery
   - immediately raise a question in viewer's mind

2. FIRST QUESTION
   - introduce a mystery that demands explanation

3. PARTIAL ANSWER
   - give some information but NOT the full truth

4. NEW BIGGER QUESTION
   - reveal something unexpected that deepens the mystery

5. ESCALATION
   - raise stakes, consequences, danger, or global impact

6. SURPRISE TWIST
   - reveal something viewers did not expect

7. DEEPER REVELATION
   - connect the twist to the larger story

8. SECOND TWIST
   - introduce a new shocking element

9. MAXIMUM STAKES
   - explain why this matters for the future, humanity, or the world

10. FINAL REVEAL
   - resolve the central mystery with a powerful insight

Topic:
{topic}
"""

        data = groq_chat(prompt)

        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")
        

        return data["choices"][0]["message"]["content"]

    return retry_request(call)


# =========================
# SCRIPT GENERATION
# =========================

def generate_script(topic, outline):

    def call():

        prompt = f"""
Write a cinematic YouTube narration.

Length: 1300-1500 words.

Retention rules:

RETENTION ENGINEERING RULES:

The script must follow strict viewer-retention mechanics.

1. HOOK (first 10 seconds)
   - shocking idea, mystery, or impossible claim
   - must instantly trigger curiosity

2. CURIOSITY LOOPS
   - every section must raise a question that is answered later
   - answers must reveal a deeper mystery

3. INFORMATION PACING
   Follow this pacing model:

   10% Hook
   20% Mystery building
   40% Escalation and discoveries
   20% Twists and reversals
   10% Final reveal

4. STAKES ESCALATION
   Each section must increase tension using:
   - danger
   - consequences
   - global implications
   - unexpected discoveries

5. MID-VIDEO REHOOK (~4 minutes)
   The mid-video twist must introduce a completely new perspective that changes how the viewer interprets the earlier story.
   Introduce a major twist that makes the viewer rethink the story.

Example pattern:
"But everything we thought was happening might actually be wrong."

6. PATTERN INTERRUPTS
   Regularly introduce surprising statements like:
   - "But here's the part nobody expected."
   - "Then something even stranger happened."

7. VISUAL STORYTELLING
   Write scenes the viewer can imagine.
   Use phrases like:
   - imagine this
   - picture this moment
   - scientists suddenly realized

8. SENTENCE RHYTHM
   Mix short and long sentences.
   Short sentences increase tension.

Example rhythm:
Something strange happened.

At first, nobody noticed.

Then one scientist looked closer.

What he found was terrifying.

Psychology rules:

viewer must constantly feel tension, curiosity, and anticipation
each section must raise a question that is answered later
use storytelling pacing similar to viral documentaries


EMOTIONAL TRAJECTORY:

The viewer's emotions should evolve like this:

curiosity -> intrigue -> tension -> shock -> revelation

The story must constantly increase emotional intensity.

Rules:

NEVER sound like a lecture, textbook, or educational explanation.

Avoid:
- "first..."
- "second..."
- "in conclusion..."

The narration must feel like a suspense story unfolding in real time.

Use dramatic storytelling, curiosity, and tension instead of explanation.

No stage directions.
No narration artifacts.

Use this outline:

{outline}

Topic:
{topic}
"""

        data = groq_chat(prompt)

        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")
        

        return data["choices"][0]["message"]["content"]

    return retry_request(call)


# =========================
# SCRIPT CRITIC
# =========================

def score_script(script):

    def call():

        prompt = f"""
You are evaluating a YouTube script for viewer retention and storytelling power.

Score the following metrics from 1 to 10.

hook_strength
curiosity_loops
storytelling_quality
viewer_tension
pattern_interrupts
watchtime_potential
twists_and_reveals
information_pacing
emotional_intensity
originality

Evaluation rules:

- hook_strength: how powerful the first 10 seconds are
- curiosity_loops: how well the script creates questions that are answered later
- storytelling_quality: narrative clarity and structure
- viewer_tension: level of suspense, stakes, and anticipation
- pattern_interrupts: use of surprises that re-engage attention
- watchtime_potential: likelihood viewers watch until the end
- twists_and_reveals: strength of unexpected developments
- information_pacing: whether information is revealed at the right speed
- emotional_intensity: emotional escalation throughout the story
- originality: uniqueness of the narrative

Also identify structural weaknesses such as:

- where viewers may lose interest
- where pacing slows
- where curiosity loops fail
- where tension drops

Script:
{script}

Return STRICT JSON using this schema:

{{
  "overall": number,
  "hook_strength": number,
  "curiosity_loops": number,
  "storytelling_quality": number,
  "viewer_tension": number,
  "pattern_interrupts": number,
  "watchtime_potential": number,
  "twists_and_reveals": number,
  "information_pacing": number,
  "emotional_intensity": number,
  "originality": number,
  "weaknesses": ["text"],
  "improvement_suggestions": ["text"]
}}

Return ONLY JSON. Do not include explanations.
"""

        data = groq_chat(prompt)

        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")

        return safe_json(data["choices"][0]["message"]["content"])

    return retry_request(call)


# =========================
# SCRIPT REWRITE ENGINE
# =========================

def rewrite_script(script, critique):

    prompt = f"""
Improve this YouTube script.

Script:
{script}

Critique:
{critique}

Fix weaknesses while keeping the core story.

Improve the script by fixing the weaknesses identified.

Specifically increase:

- curiosity loops
- narrative tension
- emotional stakes
- surprise moments
- viewer anticipation
- pacing speed
- pattern interrupts

Ensure every section raises a question that is answered later.

Do NOT remove the core story.
Only strengthen engagement.
"""

    data = groq_chat(prompt)

    if not data or "choices" not in data:
        raise Exception("Groq API returned invalid response")
    

    return data["choices"][0]["message"]["content"]


# =========================
# METADATA
# =========================

def generate_metadata(script):

    def call():

        prompt = f"""
Create a YouTube title, description and hashtags for a viral video.

TITLE RULES (CRITICAL):

Titles must follow a curiosity gap formula:

MYSTERY + CONSEQUENCE

The viewer must feel they need to know the answer.

Example styles:

"The Discovery Under Antarctica That Terrified Scientists"

"The AI Experiment That Almost Went Too Far"

"The Secret Technology Scientists Didn't Expect"

Bad example:
"Scientists Discovered Something Under Antarctica"

Good example:
"The Discovery Under Antarctica That Terrified Scientists"

Title requirements:

- 55–65 characters
- maximize curiosity
- hint at a shocking revelation
- avoid generic wording
- create tension
- make the viewer feel something important is hidden

DESCRIPTION:

Write a compelling description that expands the mystery without revealing the full answer.

HASHTAGS:

Add relevant hashtags for discovery and technology topics.

Script:
{script}

Return JSON in this format:

{{
 "title": "",
 "description": "",
 "hashtags": []
}}
"""

        data = groq_chat(prompt)

        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")
        

        return safe_json(data["choices"][0]["message"]["content"])

    return retry_request(call)



def generate_full_video_package(topic):

    def call():

        prompt = f"""
Create a viral YouTube video package.

Topic:
{topic}

Generate ALL of the following:

1) High retention outline (8–10 min video)

2) Full cinematic narration script (1300–1500 words)

3) YouTube metadata

TITLE RULES:
55–65 characters
curiosity gap
mystery + consequence

Return STRICT JSON:

{{
 "outline": "",
 "script": "",
 "title": "",
 "description": "",
 "hashtags": []
}}

"""

        data = groq_chat(prompt)

        return safe_json(data["choices"][0]["message"]["content"])

    return retry_request(call)

# =========================
# KAGGLE EXECUTION
# =========================

def setup_kaggle_auth():

    if not KAGGLE_USERNAME or not KAGGLE_KEY:
        print("Kaggle credentials missing; skipping Kaggle auth setup.")
        return False

    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)

    kaggle_json = {
        "username": KAGGLE_USERNAME,
        "key": KAGGLE_KEY
    }

    with open(kaggle_dir / "kaggle.json","w") as f:
        json.dump(kaggle_json, f)

    os.chmod(kaggle_dir / "kaggle.json", 0o600)
    return True


def send_to_kaggle(script):

    if not setup_kaggle_auth():
        return False

    Path("kaggle_pipeline").mkdir(exist_ok=True)

    with open("kaggle_pipeline/transcript.txt", "w") as f:
        f.write(script or "")

    pushed = False

    for i in range(2):
        try:
            subprocess.run(
                ["kaggle", "kernels", "push", "-p", "kaggle_pipeline"],
                check=True
            )
            pushed = True
            break
        except Exception as e:
            print("Kaggle push retry:", e)
            time.sleep(5)

    if not pushed:
        print("Kaggle kernel push failed; continuing pipeline without remote render.")
        return False

    print("Notebook pushed. Waiting for execution...")

    kernel = f"{KAGGLE_USERNAME}/ai-video-factory"

    start_time = time.time()

    time.sleep(10)

    while True:

        try:
            result = subprocess.check_output(
                ["kaggle", "kernels", "status", kernel]
            ).decode()
        except Exception as e:
            print("Unable to read Kaggle kernel status:", e)
            return False

        print(result)

        lower = result.lower()

        if "complete" in lower:
            print("Kaggle kernel finished successfully.")
            break

        if "error" in lower:
            print("Kaggle reported ERROR status. Attempting output download anyway.")
            break

        if time.time() - start_time > KAGGLE_TIMEOUT:
            print("Kaggle kernel timeout reached; continuing.")
            return False

        time.sleep(30)

    print("Attempting to download kernel outputs...")

    try:
        subprocess.run(
            [
                "kaggle",
                "kernels",
                "output",
                kernel,
                "-p",
                "artifacts"
            ],
            check=True
        )
        print("Artifacts downloaded successfully.")
        return True

    except Exception as e:
        print(f"Kaggle kernel finished but artifact download failed: {e}")
        return False


def ensure_kaggle_dataset_publish():
    if not setup_kaggle_auth():
        return False

    dataset_slug = os.getenv("KAGGLE_DATASET_SLUG", "open-university-video-input")
    owner_slug = f"{KAGGLE_USERNAME}/{dataset_slug}"

    input_dir = Path("kaggle_pipeline/input")
    input_dir.mkdir(parents=True, exist_ok=True)

    transcript_src = Path("kaggle_pipeline/transcript.txt")
    if transcript_src.exists():
        shutil.copyfile(transcript_src, input_dir / "transcript.txt")
    elif not (input_dir / "transcript.txt").exists():
        (input_dir / "transcript.txt").write_text("pipeline executed")

    metadata_path = input_dir / "dataset-metadata.json"
    if not metadata_path.exists():
        metadata_path.write_text(json.dumps({
            "title": "Open University Video Input",
            "id": owner_slug,
            "licenses": [{"name": "CC0-1.0"}]
        }, indent=2))

    status = subprocess.run(["kaggle", "datasets", "status", owner_slug], capture_output=True, text=True)

    if status.returncode != 0:
        print(f"Dataset {owner_slug} does not exist yet. Creating it.")
        create = subprocess.run(["kaggle", "datasets", "create", "-p", str(input_dir), "--dir-mode", "zip"])
        if create.returncode != 0:
            print("Failed to create Kaggle dataset.")
            return False

    version = subprocess.run(["kaggle", "datasets", "version", "-p", str(input_dir), "-m", "auto update", "--dir-mode", "zip"])
    if version.returncode != 0:
        print("Failed to version Kaggle dataset.")
        return False

    print("Kaggle dataset upload succeeded.")
    return True


# =========================
# YOUTUBE AUTH
# =========================

def youtube_client():

    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET
    )

    return build("youtube","v3",credentials=creds)


# =========================
# VIDEO + THUMBNAIL UPLOAD
# =========================

def upload_video(video_file, title, description, hashtags, thumbnail_path):

    try:
        youtube = youtube_client()

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": hashtags,
                "categoryId": "28"
            },
            "status": {
                "privacyStatus": "public"
            }
        }

        media = MediaFileUpload(video_file)

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = request.execute()

        video_id = response["id"]

        print("Uploaded video id:", video_id)

        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        return True

    except Exception as e:
        print(f"YouTube upload failed but pipeline will continue: {e}")
        return False


# =========================
# PIPELINE
# =========================

def run_pipeline():

    topics = discover_trending_topics()

    if not topics:
        topics = FALLBACK_TOPICS

    for i in range(VIDEOS_PER_DAY):

        try:
            topic = topics[i] if i < len(topics) else FALLBACK_TOPICS[i % len(FALLBACK_TOPICS)]

            print("Processing:", topic)

            package = retry_request(
                lambda: generate_full_video_package(topic),
                attempts=2,
                context="full-video-package",
                fallback={}
            ) or {}

            outline = package.get("outline", f"Outline unavailable for topic: {topic}")
            script = package.get("script", f"Script unavailable for topic: {topic}")

            title = package.get("title", topic[:90])
            description = package.get("description", f"Automated video package for: {topic}")
            hashtags = package.get("hashtags", ["AI", "Documentary", "Education"])

            thumbnail_prompt = generate_thumbnail_prompt(title)
            thumbnail_path = generate_thumbnail(thumbnail_prompt)

            send_to_kaggle(script)

            videos = glob.glob("artifacts/**/*.mp4", recursive=True)

            if not videos:
                print("No video found in Kaggle artifacts; skipping YouTube upload for this topic.")
                continue

            video_path = videos[0]

            print("Video found:", video_path)

            upload_video(
                video_path,
                title,
                description,
                hashtags,
                thumbnail_path
            )
        except Exception as e:
            print(f"Topic processing failed but continuing pipeline: {e}")


def main():
    try:
        run_pipeline()
    except Exception as e:
        print(f"Top-level pipeline failure converted to soft failure: {e}")
    finally:
        try:
            ensure_kaggle_dataset_publish()
        except Exception as e:
            print(f"Final Kaggle dataset publish failed softly: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
