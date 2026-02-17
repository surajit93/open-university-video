#scripts/generate_narration.py
import json, os, sys, re
from pathlib import Path
from groq import Groq
from collections import OrderedDict

# ============================
# CONFIG
# ============================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

SLIDE_PLAN_FILE = Path("slide_plan.json")
SLIDE_AUDIO_MAP_FILE = Path("slide_audio_map.json")
SCRIPT_FILE = Path("script.txt")

# 🔥 NEW: topic metadata injection (additive only)
CURRENT_TOPIC_FILE = Path("current_topic.json")

MIN_WORDS = 750

# ============================
# SAFE JSON EXTRACTION
# ============================

def extract_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        print("❌ No JSON object found in LLM output")
        print(text[:1000])
        raise ValueError("No JSON object found")

    return json.loads(match.group(0))


# ============================
# 🔧 NARRATION NORMALIZATION
# ============================

def normalize_narration(narration: list, slides: list) -> list:
    merged = OrderedDict()

    for entry in narration:
        sid = entry.get("slide_id")
        text = entry.get("spoken_text", "").strip()

        if sid not in merged:
            merged[sid] = []
        if text:
            merged[sid].append(text)

    normalized = []
    for slide in slides:
        sid = slide["slide_id"]
        if sid not in merged:
            print(f"ERROR: missing narration for slide {sid}")
            sys.exit(1)

        normalized.append({
            "slide_id": sid,
            "spoken_text": "\n\n".join(merged[sid])
        })

    return normalized


# ============================
# 🔥 NEW: LOAD TOPIC CONTEXT
# ============================

def load_topic_context():
    if not CURRENT_TOPIC_FILE.exists():
        return {}

    try:
        topic = json.loads(
            CURRENT_TOPIC_FILE.read_text(encoding="utf-8")
        )
        return topic
    except Exception:
        return {}


# ============================
# MAIN
# ============================

def main():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY missing or empty")
        sys.exit(1)

    if not SLIDE_PLAN_FILE.exists():
        print("ERROR: slide_plan.json missing")
        sys.exit(1)

    slides = json.loads(
        SLIDE_PLAN_FILE.read_text(encoding="utf-8")
    ).get("slides")

    if not slides or not isinstance(slides, list):
        print("ERROR: slides missing or invalid in slide_plan.json")
        sys.exit(1)

    # 🔥 Load engineered topic metadata
    topic = load_topic_context()

    retention_type = topic.get("retention_type", "standard")
    primary_persona = topic.get("primary_persona", "general_viewer")
    open_loop_required = topic.get("open_loop_required", False)
    cliffhanger_required = topic.get("cliffhanger_required", False)
    outline = topic.get("outline", "")
    title = topic.get("title", "")

    client = Groq(api_key=GROQ_API_KEY)

    # ============================
    # 🔥 ENGINEERED PROMPT
    # ============================

    prompt = f"""
Generate ONLY narration JSON.

Video Title:
{title}

Primary Persona:
{primary_persona}

Retention Type:
{retention_type}

Narrative Outline:
{outline}

Slides:
{json.dumps(slides, indent=2)}

STRICT FORMAT:
{{
  "narration": [
    {{
      "slide_id": 1,
      "spoken_text": ""
    }}
  ]
}}

Hard Rules:
- Total words >= {MIN_WORDS}
- No markdown
- No prose outside JSON
- No commentary
- Insert [PAUSE] and [SHIFT]

Retention Engineering Rules:
"""

    # 🔥 Conditional enforcement (additive only)
    if open_loop_required:
        prompt += """
- The first 15 seconds MUST create an unresolved open loop.
- Do NOT resolve that loop until mid-video.
"""

    if cliffhanger_required:
        prompt += """
- The final slide MUST end with a forward-looking cliffhanger.
- Tease next episode or deeper layer.
"""

    prompt += """
- Use strong identity language.
- Escalate emotional intensity every few slides.
- Avoid generic explanation.
- Use real-world consequences.
"""

    # ============================
    # LLM CALL
    # ============================

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an elite high-retention YouTube script architect. Return STRICT JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6,  # 🔥 Slightly increased for emotion depth
        max_tokens=4096,
    )

    raw = resp.choices[0].message.content

    try:
        data = extract_json(raw)
    except Exception:
        sys.exit(1)

    narration_raw = data.get("narration")
    if not narration_raw or not isinstance(narration_raw, list):
        print("ERROR: narration missing or invalid")
        sys.exit(1)

    # 🔧 NORMALIZE (unchanged behavior preserved)
    narration = normalize_narration(narration_raw, slides)

    # ---------------------------
    # WRITE slide_audio_map.json
    # ---------------------------
    SLIDE_AUDIO_MAP_FILE.write_text(
        json.dumps(narration, indent=2),
        encoding="utf-8"
    )
    print("✔ slide_audio_map.json written")

    # ---------------------------
    # WRITE script.txt
    # ---------------------------
    SCRIPT_FILE.write_text(
        "\n\n".join(n["spoken_text"] for n in narration),
        encoding="utf-8"
    )
    print("✔ script.txt written")


if __name__ == "__main__":
    main()
