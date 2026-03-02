#!/usr/bin/env python3
"""
AUTO CONTENT MACHINE — ENTERPRISE ADAPTIVE RETENTION INTELLIGENCE ENGINE

(ALL PREVIOUS FEATURES PRESERVED — NO FUNCTIONAL REGRESSION)

New Additions:
- YouTube Analytics Retention Graph Ingestion
- Drop-off Collapse Detection
- Script Mutation Memory
- Emotional Arc Diversity Engine
- Audience Archetype Modeling
- Contradiction Escalation Logic
- SSML Vocal Modulation + Micro Pauses
- Waveform-Based Scene Pacing
- Thumbnail A/B CTR Tracking
- Title CTR Adaptive Scoring
- Multi-Source Media Retrieval (Pexels + News)
"""

# ================= ORIGINAL IMPORTS (PRESERVED) =================

import os
import re
import json
import time
import math
import random
import logging
import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from moviepy import VideoFileClip

import requests
# ================= ENTERPRISE EXPANSION IMPORTS =================

import statistics
import uuid
import shutil
from collections import defaultdict

# ==========================================================
# NON-DETERMINISTIC CHAOS ENGINE
# ==========================================================

CHAOS_LEVELS = ["mild", "moderate", "aggressive"]

def select_chaos_level():
    return random.choices(
        CHAOS_LEVELS,
        weights=[0.4, 0.4, 0.2]
    )[0]

def inject_structural_chaos(scenes):
    chaos = select_chaos_level()

    if chaos == "mild":
        random.shuffle(scenes[int(len(scenes)*0.2):int(len(scenes)*0.6)])

    elif chaos == "moderate":
        pivot = random.randint(2, len(scenes)-3)
        scenes.insert(pivot, {
            "text": "Wait. Everything you believe about this is wrong.",
            "emotion": "shock",
            "intensity": 1.0
        })

    elif chaos == "aggressive":
        random.shuffle(scenes)
        scenes[0]["intensity"] = 1.0

    return scenes

# ==========================================================
# MULTI-ARMED BANDIT (THOMPSON SAMPLING)
# ==========================================================

def initialize_bandit(memory):
    if "thumbnail_bandit" not in memory:
        memory["thumbnail_bandit"] = {
            "arms": {},
        }

def register_thumbnail_arm(memory, thumb_id):
    initialize_bandit(memory)
    if thumb_id not in memory["thumbnail_bandit"]["arms"]:
        memory["thumbnail_bandit"]["arms"][thumb_id] = {
            "success": 1,
            "failure": 1
        }

def thompson_sampling_choice(memory):
    initialize_bandit(memory)
    arms = memory["thumbnail_bandit"]["arms"]

    sampled = {}
    for arm, data in arms.items():
        sampled[arm] = random.betavariate(
            data["success"],
            data["failure"]
        )

    if not sampled:
        return None

    return max(sampled, key=sampled.get)

def update_bandit(memory, thumb_id, ctr):
    register_thumbnail_arm(memory, thumb_id)

    if ctr > 0.08:
        memory["thumbnail_bandit"]["arms"][thumb_id]["success"] += 1
    else:
        memory["thumbnail_bandit"]["arms"][thumb_id]["failure"] += 1

# ==========================================================
# DEMOGRAPHIC SEGMENTATION ENGINE
# ==========================================================

def pull_demographics():
    try:
        creds = Credentials(
            None,
            refresh_token=YT_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=YT_CLIENT_ID,
            client_secret=YT_CLIENT_SECRET
        )

        analytics = build("youtubeAnalytics","v2",credentials=creds)

        report = analytics.reports().query(
            ids="channel==MINE",
            startDate="2023-01-01",
            endDate=datetime.utcnow().strftime("%Y-%m-%d"),
            metrics="viewerPercentage",
            dimensions="ageGroup"
        ).execute()

        return report.get("rows", [])
    except:
        return []

def determine_primary_age_group(rows):
    if not rows:
        return "25-34"

    rows_sorted = sorted(rows, key=lambda x: x[1], reverse=True)
    return rows_sorted[0][0]

def adapt_script_for_age(scenes, age_group):

    if age_group in ["13-17","18-24"]:
        modifier = "This is insane."
    elif age_group in ["45-54","55-64","65-"]:
        modifier = "The long-term consequences are serious."
    else:
        modifier = "This matters more than you think."

    for s in scenes:
        if random.random() < 0.2:
            s["text"] += " " + modifier

    return scenes

# ==========================================================
# B-ROLL VIDEO INJECTION
# ==========================================================

def fetch_youtube_broll(query):
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part":"snippet",
                "q":query,
                "type":"video",
                "maxResults":1,
                "key":YOUTUBE_DATA_API_KEY
            }
        )

        if not r.ok:
            return None

        video_id = r.json()["items"][0]["id"]["videoId"]

        # preview clip via embed fallback
        return video_id
    except:
        return None
        
        
# ==========================================================
# STATISTICAL SIGNIFICANCE FOR CTR (Z-SCORE)
# ==========================================================

def compute_z_score(p1, p2, n1=1000, n2=1000):
    try:
        p_pool = (p1*n1 + p2*n2) / (n1+n2)
        numerator = p1 - p2
        denominator = math.sqrt(p_pool*(1-p_pool)*(1/n1 + 1/n2))
        if denominator == 0:
            return 0
        return numerator / denominator
    except:
        return 0

def significant_winner(memory):
    bandit = memory.get("thumbnail_bandit", {}).get("arms", {})
    if len(bandit) < 2:
        return None

    sorted_arms = sorted(
        bandit.items(),
        key=lambda x: x[1]["success"] / (x[1]["success"] + x[1]["failure"]),
        reverse=True
    )

    top = sorted_arms[0]
    second = sorted_arms[1]

    p1 = top[1]["success"] / (top[1]["success"] + top[1]["failure"])
    p2 = second[1]["success"] / (second[1]["success"] + second[1]["failure"])

    z = compute_z_score(p1, p2)

    if z > 1.96:
        return top[0]

    return None

# ==========================================================
# DYNAMIC TRANSITION ENGINE
# ==========================================================

def dynamic_transition(clip_a, clip_b):
    style = random.choice(["crossfade", "hard_cut", "zoom_flash"])

    if style == "crossfade":
        return concatenate_videoclips(
            [clip_a.crossfadeout(0.3), clip_b.crossfadein(0.3)],
            method="compose"
        )

    elif style == "zoom_flash":
        clip_b = clip_b.resize(lambda t: 1 + 0.02*np.sin(t*10))
        return concatenate_videoclips([clip_a, clip_b], method="compose")

    else:
        return concatenate_videoclips([clip_a, clip_b], method="compose")

# ==========================================================
# NON-DETERMINISTIC PACING ENGINE
# ==========================================================

def randomized_scene_duration(base_duration):
    variance = random.uniform(-0.4, 0.4)
    duration = base_duration + (base_duration * variance)
    return max(2.5, min(duration, 7))

# ==========================================================
# TRUE CHAOS ARC BREAKER
# ==========================================================

def arc_breaker_injection(scenes):
    if random.random() < 0.35:
        idx = random.randint(2, len(scenes)-3)
        scenes.insert(idx, {
            "text": "No. Stop. That’s not even the real story.",
            "emotion": "disruption",
            "intensity": 1.0
        })
    return scenes

# ==========================================================
# ADVANCED B-ROLL STITCHING
# ==========================================================

def attempt_broll_clip(query, duration):
    video_id = fetch_youtube_broll(query)
    if not video_id:
        return None

    temp_path = CACHE / f"{video_id}.mp4"

    if not temp_path.exists():
        try:
            subprocess.run([
                "yt-dlp",
                f"https://www.youtube.com/watch?v={video_id}",
                "-f", "mp4",
                "-o", str(temp_path)
            ], check=True)
        except:
            return None

    try:
        clip = VideoFileClip(str(temp_path))
        clip = clip.subclip(0, min(duration, clip.duration))
        clip = clip.resize((1280,720))
        clip = clip.set_duration(duration)
        return clip
    except:
        return None
        
        

# ==========================================================
# ENTERPRISE VIDEO ENGINE OVERRIDE (EXTENSION ONLY)
# ==========================================================

def enterprise_compose_video(scenes, narration):

    narration_clip = AudioFileClip(str(narration))
    total_duration = narration_clip.duration
    base_duration = total_duration / len(scenes)

    final_clips = []

    for idx, s in enumerate(scenes):
        
        beats = detect_beats_from_audio(narration)

        duration = randomized_scene_duration(base_duration)

        # Beat reinforcement
        if beats:
            if idx < len(beats):
                duration = max(2.5, min(duration + 0.6, 7))

        keywords = " ".join(re.findall(r'\b\w+\b', s["text"])[:3])

        broll_clip = attempt_broll_clip(keywords, duration)

        if broll_clip:
            clip = broll_clip
        else:
            img = fetch_image(keywords)
            if img:
                clip = ImageClip(str(img)).set_duration(duration)
                clip = apply_multi_camera_motion(clip, s["intensity"], duration)
            else:
                clip = ColorClip((1280,720),(10,10,10)).set_duration(duration)

        subtitle = animated_subtitle(
            s["text"],
            duration,
            s["intensity"]
        )

        clip = CompositeVideoClip([clip, subtitle])

        final_clips.append(clip)

    # Apply dynamic transitions
    stitched = final_clips[0]
    for c in final_clips[1:]:
        stitched = dynamic_transition(stitched, c)

    stitched = stitched.set_audio(
        narration_clip.audio_fadein(1).audio_fadeout(1)
    )

    output = OUTPUT / f"video_{int(time.time())}.mp4"

    stitched.write_videofile(
        str(output),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="12000k"
    )

    return output


from pytrends.request import TrendReq
from moviepy import (
    ImageClip, AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
    TextClip
)
from moviepy.audio.fx import audio_fadein, audio_fadeout
from google.cloud import texttospeech
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import openai

# ================= CONFIG (PRESERVED) =================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

openai.api_key = OPENAI_API_KEY

ROOT = Path(".")
OUTPUT = ROOT / "output"
CACHE = ROOT / "media_cache"
MUSIC_DIR = ROOT / "assets" / "music"
MEMORY_FILE = ROOT / "engine_memory.json"

OUTPUT.mkdir(exist_ok=True)
CACHE.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("RETENTION_MACHINE")

# ================= MEMORY ENGINE =================

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {
        "collapse_points": [],
        "best_ctr_titles": [],
        "best_thumbnail_style": None,
        "archetype_success": {}
    }

def save_memory(mem):
    MEMORY_FILE.write_text(json.dumps(mem, indent=2))

# ================= ORIGINAL TREND SCORING (UNCHANGED) =================

MONETIZATION_KEYWORDS = ["ai","money","crypto","finance","future","health","war","market"]

def discover_trends():
    df = TrendReq().trending_searches(pn="united_states")
    return [str(x[0]) for x in df.head(8).values]

def get_velocity(topic):
    py = TrendReq()
    py.build_payload([topic], timeframe="now 7-d")
    data = py.interest_over_time()
    if data.empty:
        return 0.5
    vals = data[topic].tolist()
    return max(min((vals[-1] - vals[0]) / 100, 1), 0)

def news_weight(topic):
    if not NEWS_API_KEY:
        return 0.5
    r = requests.get("https://newsapi.org/v2/everything",
        params={"q":topic,"apiKey":NEWS_API_KEY})
    if not r.ok:
        return 0.5
    return min(r.json().get("totalResults",0)/1000,1)

def competition_weight(topic):
    if not YOUTUBE_DATA_API_KEY:
        return 0.5
    r = requests.get("https://www.googleapis.com/youtube/v3/search",
        params={"part":"snippet","q":topic,"type":"video",
                "maxResults":50,"key":YOUTUBE_DATA_API_KEY})
    if not r.ok:
        return 0.5
    return min(len(r.json().get("items",[]))/50,1)

def monetization_weight(topic):
    score = 0.6
    for k in MONETIZATION_KEYWORDS:
        if k in topic.lower():
            score += 0.07
    return min(score,1)

def score_topic(topic):
    return (
        get_velocity(topic)*0.35 +
        news_weight(topic)*0.2 +
        monetization_weight(topic)*0.25 +
        (1-competition_weight(topic))*0.2
    )

# ================= AUDIENCE ARCHETYPE MODEL =================

ARCHETYPES = ["fear-driven","opportunity-driven","curiosity-driven","identity-driven"]

def detect_archetype(topic, memory):
    if topic in memory["archetype_success"]:
        return memory["archetype_success"][topic]
    return random.choice(ARCHETYPES)

# ================= EMOTIONAL ARC DIVERSITY =================

ARC_TEMPLATES = [
    "escalation",
    "mystery",
    "contradiction",
    "inverted_reveal"
]

def choose_arc(memory):
    return random.choice(ARC_TEMPLATES)

# ================= SCRIPT ENGINE WITH MUTATION =================

def generate_script(topic, memory):

    # =============================
    # 1️⃣ Retrieve Adaptive Memory
    # =============================

    collapse_points = memory.get("collapse_points", [])

    archetype = detect_archetype(topic, memory)
    arc = choose_arc(memory)

    # =============================
    # Demographic Influence (NEW - Step 7)
    # =============================

    age_group = memory.get("primary_age_group", "25-34")

    age_instruction = ""
    if age_group in ["13-17", "18-24"]:
        age_instruction = """
Use fast-paced language.
Short punchy sentences.
Higher emotional spikes.
Use modern tone and urgency.
"""
    elif age_group in ["45-54", "55-64", "65-"]:
        age_instruction = """
Use deeper implications.
Slightly slower pacing.
More analytical tone.
Emphasize long-term consequences.
"""
    else:
        age_instruction = """
Balance emotional intensity with clarity.
Use persuasive but grounded tone.
"""

    # Convert collapse timestamps (0.0–1.0 ratios) into structural hints
    collapse_hints = ""
    if collapse_points:
        collapse_hints += "Previous videos showed audience drop-offs at these timeline ratios:\n"
        for cp in collapse_points:
            collapse_hints += f"- Around {cp*100:.1f}% of video length\n"

        collapse_hints += """
Avoid long exposition near these zones.
Inject pattern interrupt or contradiction before these zones.
Increase intensity spike slightly before these timestamps.
Shorten sentences around these regions.
"""

    # =============================
    # 2️⃣ Emotional Arc Mutation
    # =============================

    arc_instructions = {
        "escalation": """
Gradually increase stakes with each section.
Each scene must raise tension.
""",
        "mystery": """
Delay key reveal.
Tease incomplete explanations.
Force unresolved curiosity loops.
""",
        "contradiction": """
Introduce a strong belief.
Then break it with unexpected contradiction.
Then escalate consequences.
""",
        "inverted_reveal": """
Start with outcome.
Then rewind and explain how we got here.
Close with bigger implication.
"""
    }

    arc_instruction = arc_instructions.get(arc, "")

    # =============================
    # 3️⃣ Archetype Biasing
    # =============================

    archetype_bias = {
        "fear-driven": "Emphasize risk, danger, collapse, urgency.",
        "opportunity-driven": "Emphasize growth, leverage, advantage, upside.",
        "curiosity-driven": "Emphasize secrets, hidden forces, unknown outcomes.",
        "identity-driven": "Tie narrative to personal identity and belonging."
    }

    archetype_instruction = archetype_bias.get(archetype, "")

    # =============================
    # 4️⃣ Contradiction Escalation Injection
    # =============================

    contradiction_logic = """
At least once in the middle, introduce a surprising contradiction
that reframes the entire topic.
This must increase emotional intensity.
"""

    # =============================
    # 6️⃣ Collapse-Based Early Aggression (NEW - Step 6)
    # =============================

    early_aggression_instruction = ""

    if collapse_points and any(cp < 0.2 for cp in collapse_points):
        early_aggression_instruction = """
Very important:
Previous videos lost audience very early.
Make first 3 scenes extremely aggressive.
Short sentences.
High emotional spike.
Immediate stakes.
No slow introduction.
"""

    # =============================
    # 5️⃣ Mutation-Aware Prompt
    # =============================

    prompt = f"""
Create a high-retention YouTube script about "{topic}".

Audience Archetype: {archetype}
Narrative Arc Style: {arc}
Primary Audience Age Group: {age_group}

{arc_instruction}

{archetype_instruction}

{age_instruction}

{contradiction_logic}

{collapse_hints}

{early_aggression_instruction}

Structure requirements:
- Shock hook (first 5% extremely strong)
- Open loop
- Escalation layers
- Mid-reset spike
- Contradiction pivot
- Human impact
- Future consequences
- Personal relevance
- Hook callback ending

Scene requirements:
- Short sentences.
- Vary intensity 0.1–1.0.
- Inject curiosity phrases strategically.
- Use pattern interrupts before historical drop-off zones.

Return JSON list:
[
  {{"text":"...", "emotion":"...", "intensity":0.1}}
]
"""

    # =============================
    # 6️⃣ LLM Call
    # =============================

    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}],
        temperature=0.92
    )

    scenes = json.loads(resp["choices"][0]["message"]["content"])

    # =============================
    # 7️⃣ Post-Generation Structural Reinforcement
    # =============================

    total = len(scenes)

    for idx, scene in enumerate(scenes):

        position_ratio = idx / total

        # If scene falls near previous collapse region, force spike
        for cp in collapse_points:
            if abs(position_ratio - cp) < 0.05:
                scene["intensity"] = min(scene["intensity"] + 0.25, 1.0)
                scene["text"] += " But here's the part nobody expects."

        # Ensure first scene is dominant hook
        if idx == 0:
            scene["intensity"] = 0.98

        # Extra reinforcement if early collapse historically happened
        if collapse_points and any(cp < 0.2 for cp in collapse_points):
            if idx < 3:
                scene["intensity"] = min(1.0, scene["intensity"] + 0.15)

        # Ensure final callback spike
        if idx == total - 1:
            scene["intensity"] = 1.0

    return scenes

# ================= RETENTION GRAPH INGESTION =================

def pull_retention_graph(video_id):
    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET
    )

    analytics = build("youtubeAnalytics","v2",credentials=creds)

    report = analytics.reports().query(
        ids="channel==MINE",
        startDate="2023-01-01",
        endDate=datetime.utcnow().strftime("%Y-%m-%d"),
        metrics="audienceWatchRatio",
        dimensions="elapsedVideoTimeRatio",
        filters=f"video=={video_id}"
    ).execute()

    return report
    
def pull_ctr_metrics(video_id):
    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET
    )

    analytics = build("youtubeAnalytics","v2",credentials=creds)

    report = analytics.reports().query(
        ids="channel==MINE",
        startDate="2023-01-01",
        endDate=datetime.utcnow().strftime("%Y-%m-%d"),
        metrics="impressions,impressionsCtr",
        filters=f"video=={video_id}"
    ).execute()

    rows = report.get("rows", [])
    if not rows:
        return None, None

    impressions = rows[0][0]
    ctr = rows[0][1]

    return impressions, ctr    

def detect_collapse_points(report):
    collapse = []
    rows = report.get("rows", [])
    for i in range(1, len(rows)):
        if rows[i][1] < rows[i-1][1] * 0.7:
            collapse.append(rows[i][0])
    return collapse

# ================= SSML AUDIO PSYCHOLOGY =================

def build_ssml_script(scenes):
    ssml = "<speak>"
    for s in scenes:
        rate = 1.0 + (s["intensity"] * 0.2)
        ssml += f'<prosody rate="{rate}">'
        ssml += s["text"]
        ssml += '</prosody><break time="400ms"/>'
    ssml += "</speak>"
    return ssml

def generate_narration(text):
    client = texttospeech.TextToSpeechClient()

    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(ssml=text),
        voice=texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-D"
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0
        )
    )

    out = OUTPUT / "narration.wav"
    with open(out,"wb") as f:
        f.write(response.audio_content)
    return out

# ================= MULTI SOURCE MEDIA =================

def fetch_news_image(topic):
    if not NEWS_API_KEY:
        return None
    r = requests.get("https://newsapi.org/v2/everything",
        params={"q":topic,"apiKey":NEWS_API_KEY,"pageSize":1})
    if not r.ok:
        return None
    articles = r.json().get("articles",[])
    if not articles:
        return None
    img_url = articles[0].get("urlToImage")
    if not img_url:
        return None
    path = CACHE / f"news_{hash(topic)}.jpg"
    if not path.exists():
        with open(path,"wb") as f:
            f.write(requests.get(img_url).content)
    return path

def fetch_image(query):
    news_img = fetch_news_image(query)
    if news_img:
        return news_img

    headers={"Authorization":PEXELS_API_KEY}
    r=requests.get("https://api.pexels.com/v1/search",
        headers=headers,
        params={"query":query,"per_page":1})
    if not r.ok:
        return None
    url=r.json()["photos"][0]["src"]["large"]
    path=CACHE/f"{hash(query)}.jpg"
    if not path.exists():
        with open(path,"wb") as f:
            f.write(requests.get(url).content)
    return path

# ================= THUMBNAIL A/B TRACKING =================

def generate_thumbnail_variants(topic):
    variants = []
    for word in ["SHOCKING","BREAKING","FUTURE"]:
        img = ColorClip((1280,720),(0,0,0))
        path = OUTPUT / f"thumb_{word}.jpg"
        img.save_frame(str(path))
        variants.append(path)
    return variants

# ================= VIDEO ENGINE (UNCHANGED CORE + EXTENDED) =================

# ================= ADDITIONAL IMPORTS (NO REMOVAL) =================

import numpy as np
from scipy.io import wavfile

# ================= BEAT DETECTION ENGINE =================

def detect_beats_from_audio(audio_path):
    try:
        rate, data = wavfile.read(str(audio_path))
        if len(data.shape) > 1:
            data = data[:,0]

        window = int(rate * 0.1)
        energy = []

        for i in range(0, len(data), window):
            segment = data[i:i+window]
            energy.append(np.sum(np.abs(segment)))

        threshold = np.mean(energy) * 1.5
        beats = [i for i, e in enumerate(energy) if e > threshold]

        return beats
    except:
        return []

# ================= SILENCE BEFORE REVEAL =================

def inject_silence_before_reveal(ssml_script):
    return ssml_script.replace(
        "But here",
        '<break time="700ms"/>But here'
    )

# ================= HOOK A/B TESTING =================

def generate_hook_variants(topic):
    prompt = f"Generate 3 high-retention opening hooks for a YouTube video about {topic}"
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}]
    )
    hooks = resp["choices"][0]["message"]["content"].split("\n")
    return [h for h in hooks if len(h.strip()) > 10][:3]

def select_best_hook(hooks, memory):
    if memory.get("best_ctr_titles"):
        return memory["best_ctr_titles"][0]
    return random.choice(hooks)

# ================= CTR ADAPTIVE TITLE =================

def update_title_memory(title, ctr, memory):
    memory["best_ctr_titles"].append((title, ctr))
    memory["best_ctr_titles"] = sorted(
        memory["best_ctr_titles"],
        key=lambda x: x[1],
        reverse=True
    )[:5]

# ================= MID-VIDEO CLIFFHANGER =================

def inject_mid_cliffhanger(scenes):
    total = len(scenes)
    target = int(total * 0.35)

    scenes[target]["text"] += " And what happens next changes everything."
    scenes[target]["intensity"] = 1.0

    return scenes

# ================= MULTI CAMERA MOTION =================

def apply_multi_camera_motion(clip, intensity, duration):

    base_zoom = 1 + intensity * 0.04
    oscillation = 0.01 * intensity

    def motion(t):
        return 1 + base_zoom * t/duration + oscillation*np.sin(t*2)

    return clip.resize(lambda t: motion(t))

# ================= SUBTITLE ANIMATION =================

def animated_subtitle(text, duration, intensity):

    base_size = 40 + int(intensity*20)

    subtitle = TextClip(
        text[:80],
        fontsize=base_size,
        color='white'
    )

    subtitle = subtitle.set_position(
        lambda t: ("center", 600 + int(10*np.sin(t*3)))
    ).set_duration(duration)

    return subtitle

# ================= ENHANCED VIDEO ENGINE =================

def compose_video(scenes,narration):

    narration_clip=AudioFileClip(str(narration))
    beats = detect_beats_from_audio(narration)

    clips=[]
    total_duration=narration_clip.duration
    per_scene=total_duration/len(scenes)

    for idx,s in enumerate(scenes):

        keywords=" ".join(re.findall(r'\b\w+\b',s["text"])[:3])
        img=fetch_image(keywords)
        duration=per_scene

        if img:
            clip=ImageClip(str(img)).set_duration(duration)
            clip=apply_multi_camera_motion(clip,s["intensity"],duration)
        else:
            clip=ColorClip((1280,720),(10,10,10)).set_duration(duration)

        subtitle=animated_subtitle(
            s["text"],
            duration,
            s["intensity"]
        )

        clip=CompositeVideoClip([clip,subtitle])

        # Hard visual cut every 3–5 seconds
        if duration > 5:
            clip = clip.subclip(0, min(duration,5))

        clips.append(clip)

    final=concatenate_videoclips(clips,method="compose")

    final=final.set_audio(
        narration_clip.audio_fadein(1).audio_fadeout(1)
    )

    output=OUTPUT/f"video_{int(time.time())}.mp4"
    final.write_videofile(
        str(output),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="12000k"
    )

    return output

def delayed_retention_update():
    memory = load_memory()

    if "last_uploaded_video" not in memory:
        return

    video_id = memory["last_uploaded_video"]

    try:
        report = pull_retention_graph(video_id)
        collapse_points = detect_collapse_points(report)
        memory["collapse_points"] = collapse_points
        save_memory(memory)
        log.info("Delayed retention learning complete")
    except:
        pass

def upload_to_youtube(video_path, title, description, thumbnail_path):

    creds = Credentials(
        None,
        refresh_token=YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YT_CLIENT_ID,
        client_secret=YT_CLIENT_SECRET
    )

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "28"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(
        str(video_path),
        chunksize=-1,
        resumable=True
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()

    video_id = response["id"]

    # Upload thumbnail
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=str(thumbnail_path)
    ).execute()

    return video_id
# ================= MAIN =================

def run():

    memory = load_memory()

    trends = discover_trends()
    scored = [(t, score_topic(t)) for t in trends]
    topic = sorted(scored, key=lambda x:x[1], reverse=True)[0][0]
    # ================= THUMBNAIL BANDIT SETUP =================

    thumbnail_variants = generate_thumbnail_variants(topic)

    initialize_bandit(memory)

    for thumb in thumbnail_variants:
        register_thumbnail_arm(memory, str(thumb))

    chosen_thumb = thompson_sampling_choice(memory)

    if not chosen_thumb:
        chosen_thumb = str(thumbnail_variants[0])

    log.info(f"Selected Topic: {topic}")

    hooks = generate_hook_variants(topic)
    best_hook = select_best_hook(hooks, memory)

    scenes = generate_script(topic, memory)

    # Force best hook into first scene
    if scenes:
        scenes[0]["text"] = best_hook
        scenes[0]["intensity"] = 1.0

    # Non-deterministic injection
    scenes = inject_structural_chaos(scenes)
    scenes = arc_breaker_injection(scenes)
    scenes = inject_mid_cliffhanger(scenes)

    # Demographic adaptation
    demo = pull_demographics()
    age_group = determine_primary_age_group(demo)
    scenes = adapt_script_for_age(scenes, age_group)
    
    memory["primary_age_group"] = age_group

    ssml_script = build_ssml_script(scenes)
    ssml_script = inject_silence_before_reveal(ssml_script)

    narration = generate_narration(ssml_script)

    video = enterprise_compose_video(scenes, narration)

    title = f"{topic} — What They’re Not Telling You"
    description = f"Full breakdown of {topic}. Future impact, hidden forces, and what it means for you."

    video_id = upload_to_youtube(video, title, description, chosen_thumb)

    log.info("VIDEO UPLOADED")
    
    memory["last_uploaded_video"] = video_id

    # Simulate CTR learning (replace with real metric pull later)
    try:
        impressions, real_ctr = pull_ctr_metrics(video_id)

        if real_ctr:
            update_bandit(memory, chosen_thumb, real_ctr)
            update_title_memory(title, real_ctr, memory)
    except:
        pass
        
    # ================= AUTO THUMBNAIL REPLACEMENT =================

    winner = significant_winner(memory)

    if winner and winner != chosen_thumb:
        try:
            creds = Credentials(
                None,
                refresh_token=YT_REFRESH_TOKEN,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=YT_CLIENT_ID,
                client_secret=YT_CLIENT_SECRET
            )

            youtube = build("youtube", "v3", credentials=creds)

            youtube.thumbnails().set(
                videoId=video_id,
                media_body=str(winner)
            ).execute()

            log.info("Thumbnail replaced with statistical winner")

        except:
            pass        

    # Retention learning
    try:
        report = pull_retention_graph(video_id)
        collapse_points = detect_collapse_points(report)
        memory["collapse_points"] = collapse_points
    except:
        pass

    save_memory(memory)

if __name__=="__main__":
    if os.getenv("MODE") == "retention_update":
        delayed_retention_update()
    else:
        run()
