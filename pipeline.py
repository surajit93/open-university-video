import os
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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
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

# NEW SAFETY LIMITS
MAX_SCRIPT_REWRITES = 6
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


def retry_request(func, attempts=3):
    for i in range(attempts):
        try:
            return func()
        except Exception as e:
            print("Retry:", e)
            time.sleep(3)
    raise Exception("Max retries reached")


# NEW: API PROTECTION
def safe_api_json(r):

    try:
        data = r.json()
    except:
        raise Exception("API returned invalid JSON")

    if "choices" not in data:
        raise Exception(f"Malformed API response: {data}")

    return data


# =========================
# THUMBNAIL PROMPT
# =========================

def generate_thumbnail_prompt(title):

    def call():

        prompt = f"""
Create a highly clickable YouTube thumbnail concept.

Video title:
{title}

Return a short visual description suitable for generating a thumbnail image.
Focus on:

emotion
contrast
dramatic lighting
large subject
high curiosity
"""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"gpt-4o",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        data = safe_api_json(r)

        return data["choices"][0]["message"]["content"]

    return retry_request(call)


# =========================
# THUMBNAIL GENERATION
# =========================

def generate_thumbnail(prompt):

    def call():

        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-image-1",
                "prompt": prompt,
                "size": "1024x1024"
            }
        )

        data = r.json()

        if "data" not in data:
            raise Exception("Thumbnail generation failed")

        image_url = data["data"][0]["url"]

        img = requests.get(image_url).content

        Path("artifacts").mkdir(exist_ok=True)

        with open("artifacts/thumbnail.png","wb") as f:
            f.write(img)

        return "artifacts/thumbnail.png"

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

Topics:
{topics}

Return list only.
"""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"gpt-4o",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        data = safe_api_json(r)

        angles = data["choices"][0]["message"]["content"].split("\n")

        return [x.strip("- ").strip() for x in angles if x]

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

        print("No external trends found. Using fallback topics.")

        seeds = [
            "Artificial Intelligence breakthroughs",
            "Future of robotics",
            "Space exploration discoveries",
            "New scientific discoveries",
            "Technology changing the world",
            "Mysteries of the universe",
            "Future of human civilization",
            "Hidden technologies shaping society"
        ]

    seeds = seeds[:15]

    print("Seed topics:", seeds)

    def expand_topics():

        prompt = f"""
Expand each topic into multiple viral YouTube angles.

Goal:
Find angles capable of getting 1M+ views.

Seeds:
{seeds}

Return list only.
"""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        return safe_api_json(r)

    expanded = retry_request(expand_topics)["choices"][0]["message"]["content"]

    expanded = expanded.split("\n")
    expanded = [x.strip("- ").strip() for x in expanded if x]

    print("Expanded topics:", expanded)

    angles = generate_angles(expanded)

    print("Generated angles:", angles)

    def rank_topics():

        prompt = f"""
Rank these YouTube topics for viral potential.

Consider:
curiosity
controversy
global interest
story potential
future impact

Topics:
{angles}

Return ranked list.
"""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"gpt-4o",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        return safe_api_json(r)

    ranked = retry_request(rank_topics)["choices"][0]["message"]["content"]

    ranked = ranked.split("\n")
    ranked = [x.strip("- ").strip() for x in ranked if x]

    print("Top topics:", ranked)

    return ranked[:VIDEOS_PER_DAY]


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

Include:
Hook
Open loops
Twists
Escalation
Final reveal

Topic:
{topic}
"""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"gpt-4o",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        return safe_api_json(r)

    data = retry_request(call)

    return data["choices"][0]["message"]["content"]


# =========================
# SCRIPT GENERATION
# =========================

def generate_script(topic, outline):

    def call():

        prompt = f"""
Write a cinematic YouTube narration.

Length: 1300-1500 words.

Retention rules:

1 powerful hook in first 10 seconds
curiosity trigger every 20 seconds
open loops introduced throughout
minimum 3 twists
mid-video rehook at ~4 minutes
strong final payoff

Rules:
no stage directions
no narration artifacts

Use this outline:

{outline}

Topic:
{topic}
"""

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"mixtral-8x7b-32768",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        return safe_api_json(r)

    data = retry_request(call)

    return data["choices"][0]["message"]["content"]


# =========================
# SCRIPT CRITIC
# =========================

def score_script(script):

    def call():

        prompt = f"""
Evaluate this YouTube script.

Score the following 1-10.

curiosity
storytelling
engagement
watchtime potential
originality
hook strength
open loops
twists
information density
pacing

Script:
{script}

Return JSON with overall score.
"""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"gpt-4o",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        return safe_api_json(r)

    data = retry_request(call)

    return safe_json(data["choices"][0]["message"]["content"])


# =========================
# SCRIPT REWRITE ENGINE
# =========================

def rewrite_script(script, critique):

    prompt = f"""
Improve this YouTube script.

Critique:
{critique}

Fix weaknesses while keeping the core story.
"""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model":"gpt-4o",
            "messages":[{"role":"user","content":prompt}]
        }
    )

    data = safe_api_json(r)

    return data["choices"][0]["message"]["content"]


# =========================
# METADATA
# =========================

def generate_metadata(script):

    def call():

        prompt = f"""
Create YouTube title, description and hashtags.

Script:
{script}

Return JSON
"""

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model":"mixtral-8x7b-32768",
                "messages":[{"role":"user","content":prompt}]
            }
        )

        return safe_api_json(r)

    data = retry_request(call)

    return safe_json(data["choices"][0]["message"]["content"])


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

    # retry push
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

        while score < 9 and rewrites < MAX_SCRIPT_REWRITES:

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
