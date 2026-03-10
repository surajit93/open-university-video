import os
import re
import json
import time
import subprocess
import requests
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


def retry_request(func, attempts=6):

    for i in range(attempts):

        try:
            return func()

        except Exception as e:

            if "RATE_LIMIT" in str(e):
                wait = 6 + i*3
                print(f"Rate limited. Waiting {wait}s")
                time.sleep(wait)
            else:
                print("Retry:", e)
                time.sleep(3)

    raise Exception("Max retries reached")


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
    time.sleep(3)

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

    return retry_request(call)


# =========================
# THUMBNAIL IMAGE
# =========================

def generate_thumbnail(prompt):

    def call():

        api = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        r = requests.post(api, headers=headers, json={"inputs":prompt})

        if r.status_code != 200:
            raise Exception(f"HuggingFace image error: {r.text}")

        Path("artifacts").mkdir(exist_ok=True)

        path="artifacts/thumbnail.png"

        with open(path,"wb") as f:
            f.write(r.content)

        return path

    return retry_request(call)


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

def discover_trending_topics():

    pytrend = TrendReq()

    google_trends = []

    try:

        google = pytrend.trending_searches(pn="US")

        google_trends = list(google[0:15][0])

        print("Google trends:", google_trends)

    except Exception as e:

        print("Google Trends failed:", e)

        google_trends = []

    news_url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=20&apiKey={NEWS_API_KEY}"
    news = requests.get(news_url).json()

    news_topics = [a["title"] for a in news.get("articles", [])]

    seeds = list(set(google_trends + news_topics))

    if len(seeds) == 0:

        seeds = [

            "The secret AI experiment scientists never expected to work",
            "The dangerous technology researchers say could change humanity forever",
            "The discovery scientists made that they initially refused to believe",
            "The hidden scientific experiment that produced terrifying results",
            "The mysterious signal from deep space that scientists still cannot explain",
            "The government project researchers claim was kept secret for decades",
            "The unexpected discovery scientists made while studying the universe",
            "The experiment that produced results nobody thought were possible",
            "The strange object detected in space that confused astronomers",
            "The scientific discovery that forced experts to rethink everything",
            "The technology breakthrough that scientists say could reshape civilization",
            "The mysterious anomaly discovered during a deep space mission",
            "The controversial experiment that shocked the scientific community",
            "The hidden technology researchers are quietly developing right now",
            "The unexplained cosmic signal that triggered global investigation",
            "The strange phenomenon scientists discovered while studying Earth",
            "The scientific project that produced results nobody could explain",
            "The unexpected discovery made during a high-risk experiment",
            "The experiment that revealed something surprising about human intelligence",
            "The mysterious event scientists detected but still cannot explain",
            "The strange discovery scientists made while exploring deep space",
            "The breakthrough technology that could completely change the future",
            "The unexplained signal researchers detected from far beyond our galaxy",
            "The hidden discovery scientists say could alter our understanding of reality",
            "The scientific mystery researchers are racing to solve"
        ]

    seeds = seeds[:15]

    print("Seed topics:", seeds)

    def expand_topics():

        prompt = f"""
Expand each topic into multiple viral YouTube angles.

Goal:
Find angles capable of getting 1M+ views.

Angles must include tension, mystery, or revelation.

Seeds:
{seeds}

Return list only.
"""

        return groq_chat(prompt)

    expanded = retry_request(expand_topics)["choices"][0]["message"]["content"]

    expanded = expanded.split("\n")
    expanded = [x.strip("- ").strip() for x in expanded if x]

    print("Expanded topics:", expanded)

    angles = generate_angles(expanded)

    print("Generated angles:", angles)

    # Filter for narrative tension
    angles = filter_storyworthy_topics(angles)

    print("Storyworthy topics:", angles)

    ranked = rank_topics(angles)

    print("Top topics:", ranked)

    if not ranked:
        ranked = angles

    return ranked[:VIDEOS_PER_DAY]
    
    
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

{
 "title": "",
 "description": "",
 "hashtags": []
}
"""

        data = groq_chat(prompt)

        if not data or "choices" not in data:
            raise Exception("Groq API returned invalid response")
        

        return safe_json(data["choices"][0]["message"]["content"])

    return retry_request(call)


# =========================
# KAGGLE EXECUTION
# =========================

def setup_kaggle_auth():

    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)

    kaggle_json = {
        "username": KAGGLE_USERNAME,
        "key": KAGGLE_KEY
    }

    with open(kaggle_dir / "kaggle.json","w") as f:
        json.dump(kaggle_json, f)

    os.chmod(kaggle_dir / "kaggle.json", 0o600)


def send_to_kaggle(script):

    setup_kaggle_auth()

    Path("kaggle_pipeline/input").mkdir(parents=True, exist_ok=True)

    with open("kaggle_pipeline/input/transcript.txt","w") as f:
        f.write(script)

    for i in range(3):

        try:

            subprocess.run(
                ["kaggle","kernels","push","-p","kaggle_pipeline"],
                check=True
            )

            break

        except Exception as e:

            print("Kaggle push retry:", e)

            time.sleep(10)

    print("Notebook pushed. Waiting for execution...")

    kernel = f"{KAGGLE_USERNAME}/YOUR_KERNEL"

    start_time = time.time()

    while True:

        result = subprocess.check_output(
            ["kaggle","kernels","status", kernel]
        ).decode()

        print(result)

        lower = result.lower()

        if "complete" in lower:
            break

        if "error" in lower:
            raise Exception("Kaggle kernel execution failed")

        if time.time() - start_time > KAGGLE_TIMEOUT:
            raise Exception("Kaggle kernel timeout")

        time.sleep(30)

    print("Notebook finished. Downloading output...")

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


# =========================
# PIPELINE
# =========================

def run_pipeline():

    topics = discover_trending_topics()

    for i in range(VIDEOS_PER_DAY):

        topic = topics[i]

        print("Processing:", topic)

        outline = generate_outline(topic)

        script = None
        score = 0
        rewrites = 0

        candidate = generate_script(topic, outline)

        last_score = 0

        while score < 9 and rewrites < MAX_SCRIPT_REWRITES:

            if score <= last_score:
                break

            last_score = score

            result = score_script(candidate)

            score = result.get("overall",0)

            print("Script score:", score)

            if score >= 9:
                script = candidate
                break

            candidate = rewrite_script(candidate, result)

            rewrites += 1

        script = candidate

        metadata = generate_metadata(script)

        title = metadata["title"]
        description = metadata["description"]
        hashtags = metadata["hashtags"]

        thumbnail_prompt = generate_thumbnail_prompt(title)
        thumbnail_path = generate_thumbnail(thumbnail_prompt)

        send_to_kaggle(script)

        video_path = "artifacts/final_video.mp4"

        upload_video(
            video_path,
            title,
            description,
            hashtags,
            thumbnail_path
        )


if __name__ == "__main__":
    run_pipeline()
