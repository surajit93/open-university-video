import json
import os
import sys
import re
from pathlib import Path
from groq import Groq

# ============================
# CONFIG
# ============================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

CURRENT_TOPIC_FILE = Path("current_topic.json")

SLIDE_PLAN_FILE = Path("slide_plan.json")
SLIDE_AUDIO_MAP_FILE = Path("slide_audio_map.json")
SCRIPT_FILE = Path("script.txt")

MIN_WORDS = 750
MAX_WORDS = 1400

ALLOWED_VISUALS = {
    "CONCEPT_DIAGRAM",
    "FLOW_DIAGRAM",
    "SYSTEM_DIAGRAM",
    "CODE_BLOCK",
    "MATH_FORMULA",
    "PHOTO_REFERENCE",
    "TEXT_ONLY",
}

# ============================
# LLM CALL
# ============================

def groq_generate(prompt: str) -> str:
    client = Groq(api_key=GROQ_API_KEY)

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a senior university lecturer and instructional designer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=4096,
    )

    return resp.choices[0].message.content or ""


# ============================
# JSON EXTRACTION (CRITICAL)
# ============================

def extract_json(text: str) -> dict:
    """
    Safely extract the FIRST JSON object from text.
    Handles:
    - prose before JSON
    - code fences
    - trailing text
    """

    if not text.strip():
        raise ValueError("LLM returned empty response")

    # Remove ``` blocks
    text = re.sub(r"```.*?```", "", text, flags=re.S)

    # Find first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON extracted: {e}") from e


# ============================
# PROMPT
# ============================

def build_prompt(topic: dict) -> str:
    return f"""
Produce a FULL university lecture.

Title: {topic['title']}

Outline:
{topic.get('outline','')}

Learning Objectives:
{json.dumps(topic.get('learning_objectives', []), indent=2)}

Key Questions:
{json.dumps(topic.get('key_questions', []), indent=2)}

Slide Guidance:
{topic.get('slide_guidance','')}

Expected Duration:
{topic.get('expected_duration_min', 8)} minutes

Rules:
- One idea per slide
- EXACTLY one visual strategy
- Explicit left panel plan
- 2–3 sentence right panel gist
- Calm academic narration
- Explain WHY, not just WHAT
- Insert [PAUSE] and [SHIFT]

Return STRICT JSON:
{{
  "slides": [...],
  "narration": ...
}}
"""


# ============================
# NORMALIZATION
# ============================

def normalize_narration(narration, slides):
    if isinstance(narration, dict) and "narration" in narration:
        narration = narration["narration"]

    if isinstance(narration, list):
        return narration

    if isinstance(narration, str):
        words = narration.split()
        per_slide = max(len(words) // len(slides), 120)

        out = []
        i = 0
        for s in slides:
            chunk = words[i:i+per_slide]
            i += per_slide
            out.append({
                "slide_id": s["slide_id"],
                "spoken_text": " ".join(chunk)
            })
        return out

    raise ValueError("Unsupported narration format")


# ============================
# VALIDATION
# ============================

def count_words(narration):
    return sum(len(n.get("spoken_text","").split()) for n in narration)


def validate(data):
    slides = data["slides"]
    narration = data["narration"]

    if len(slides) != len(narration):
        raise ValueError("Slides/narration mismatch")

    ids = [s["slide_id"] for s in slides]
    if ids != list(range(1, len(ids)+1)):
        raise ValueError("slide_id must be contiguous")

    if count_words(narration) < MIN_WORDS:
        raise ValueError("Narration too short")


# ============================
# MAIN
# ============================

def main():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set")
        sys.exit(1)

    topic = json.loads(CURRENT_TOPIC_FILE.read_text())

    print("Generating slides + narration (Groq)...")

    raw = groq_generate(build_prompt(topic))

    try:
        data = extract_json(raw)
    except Exception as e:
        print("❌ JSON extraction failed")
        print("----- RAW OUTPUT -----")
        print(raw)
        print("----------------------")
        raise

    data["narration"] = normalize_narration(
        data["narration"],
        data["slides"]
    )

    validate(data)

    SLIDE_PLAN_FILE.write_text(json.dumps({"slides": data["slides"]}, indent=2))
    SLIDE_AUDIO_MAP_FILE.write_text(json.dumps(data["narration"], indent=2))
    SCRIPT_FILE.write_text("\n\n".join(n["spoken_text"] for n in data["narration"]))

    print("✔ slide_plan.json written")
    print("✔ slide_audio_map.json written")
    print("✔ script.txt written")


if __name__ == "__main__":
    main()
