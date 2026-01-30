import json
import os
import sys
import requests
from pathlib import Path
import subprocess

# ============================
# CONFIG
# ============================

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_TOKEN = os.environ.get("HF_TOKEN")

CURRENT_TOPIC_FILE = Path("current_topic.json")

SLIDE_PLAN_FILE = Path("slide_plan.json")
SCRIPT_FILE = Path("script.txt")
SLIDE_AUDIO_MAP_FILE = Path("slide_audio_map.json")

CALL_COLAB_SCRIPT = Path("scripts/call_colab.py")

MIN_WORDS = 750
MAX_WORDS = 1400

# ============================
# LLM CALL
# ============================

def hf_generate(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 2200,
            "temperature": 0.4,
            "top_p": 0.9
        }
    }

    r = requests.post(HF_API_URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    raise RuntimeError("Unexpected HuggingFace response")


# ============================
# PROMPT (SINGLE CALL, TWO PHASES)
# ============================

def build_prompt(title: str, outline: str) -> str:
    return f"""
You are a senior university lecturer, instructional designer,
and visual communication expert.

You must think like a human teacher preparing a lecture.

Your task has TWO PHASES but must be answered in ONE response.

You must NOT generate images.
You must NOT generate code.
You must NOT generate rendering instructions.

────────────────────────
PHASE A — SLIDE PLANNING (TEACHER MODE)
────────────────────────

Topic:
{title}

Course Context:
{outline}

Break the topic into 3–8 slides.

For EACH slide:
- Decide the ONE idea a student must remember after 30 seconds
- Decide what confusion it removes
- Classify the content
- Choose EXACTLY ONE visual strategy
- Describe EXACTLY what appears on the LEFT panel
- Write a 2–3 sentence student-friendly GIST for the RIGHT panel

Rules:
- Prefer diagrams over photos
- Use photos ONLY if they genuinely aid understanding
- TEXT_ONLY is allowed if visuals add no value
- Never guess visuals
- Never split text into keywords

────────────────────────
PHASE B — NARRATION (NARRATOR MODE)
────────────────────────

Using ONLY the slide plans you created above:

- Write spoken academic narration
- Calm, confident, human tone
- Short sentences
- Natural flow
- No hype
- No self reference
- No phrases like "in this video"
- No bullet lists
- No emojis

Rules:
- Narration must ALIGN slide-by-slide
- Each slide must have its own narration block
- Insert pacing markers: [PAUSE], [SHIFT] when appropriate
- Total length must be between {MIN_WORDS} and {MAX_WORDS} words

────────────────────────
OUTPUT FORMAT (STRICT)
────────────────────────

Return ONLY valid JSON in this exact structure:

{{
  "slides": [
    {{
      "slide_id": 1,
      "title": "Short slide title",
      "teaching_intent": {{
        "core_idea": "",
        "student_confusion_resolved": ""
      }},
      "content_type": "",
      "visual_strategy": "",
      "left_panel_plan": {{
        "description": "",
        "diagram_boxes": [],
        "diagram_relationships": "",
        "photo_query": "",
        "code_language": "",
        "math_formula": ""
      }},
      "right_panel_gist": "",
      "layout_notes": {{
        "font_style": "very_large | large",
        "text_density": "low | medium",
        "visual_weight": "light | balanced | heavy"
      }}
    }}
  ],
  "narration": [
    {{
      "slide_id": 1,
      "spoken_text": ""
    }}
  ]
}}

No extra text. No markdown. No explanations.
"""


# ============================
# VALIDATION
# ============================

def validate_output(data: dict):
    if "slides" not in data or "narration" not in data:
        raise ValueError("Missing slides or narration")

    if len(data["slides"]) != len(data["narration"]):
        raise ValueError("Slides and narration count mismatch")

    word_count = sum(
        len(n["spoken_text"].split())
        for n in data["narration"]
    )

    if not (MIN_WORDS <= word_count <= MAX_WORDS):
        raise ValueError(f"Narration word count out of bounds: {word_count}")

# ============================
# MAIN
# ============================

def main():
    if not CURRENT_TOPIC_FILE.exists():
        print("ERROR: current_topic.json not found")
        sys.exit(1)

    if not HF_TOKEN:
        print("ERROR: HF_TOKEN not set")
        sys.exit(1)

    topic = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    title = topic["title"]
    outline = topic.get("outline", "")

    print("Generating slide plan + narration (ONE CALL)...")

    prompt = build_prompt(title, outline)
    raw = hf_generate(prompt)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("ERROR: LLM did not return valid JSON")
        sys.exit(1)

    validate_output(data)

    # --------------------
    # WRITE FILES
    # --------------------

    SLIDE_PLAN_FILE.write_text(
        json.dumps({"slides": data["slides"]}, indent=2),
        encoding="utf-8"
    )

    SCRIPT_FILE.write_text(
        "\n\n".join(n["spoken_text"] for n in data["narration"]),
        encoding="utf-8"
    )

    SLIDE_AUDIO_MAP_FILE.write_text(
        json.dumps(data["narration"], indent=2),
        encoding="utf-8"
    )

    print("slide_plan.json written")
    print("script.txt written")
    print("slide_audio_map.json written")

    # --------------------
    # TRIGGER COLAB
    # --------------------

    if CALL_COLAB_SCRIPT.exists():
        print("Triggering Colab executor...")
        subprocess.run(
            [sys.executable, str(CALL_COLAB_SCRIPT)],
            check=True
        )
    else:
        print("call_colab.py not found — skipping execution")

    print("DONE")

if __name__ == "__main__":
    main()
