import json, os, sys, re
from pathlib import Path
from groq import Groq

# ============================
# CONFIG
# ============================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"

SLIDE_PLAN_FILE = Path("slide_plan.json")
SLIDE_AUDIO_MAP_FILE = Path("slide_audio_map.json")

# transcript output for MCQ generation
SCRIPT_FILE = Path("script.txt")

MIN_WORDS = 750

# ============================
# SAFE JSON EXTRACTION
# ============================

def extract_json(text: str) -> dict:
    text = text.strip()

    # Fast path
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # Regex fallback
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        print("❌ No JSON object found in LLM output")
        print("----- RAW OUTPUT (first 1000 chars) -----")
        print(text[:1000])
        raise ValueError("No JSON object found")

    return json.loads(match.group(0))


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

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
Generate ONLY narration JSON.

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

Rules:
- Explain WHY concepts exist
- Academic tone
- Insert [PAUSE] and [SHIFT]
- Total words >= {MIN_WORDS}
- No markdown
- No prose
- No commentary
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a university lecturer. "
                    "Return STRICT JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_tokens=4096,
    )

    raw = resp.choices[0].message.content

    try:
        data = extract_json(raw)
    except Exception:
        sys.exit(1)

    narration = data.get("narration")
    if not narration or not isinstance(narration, list):
        print("ERROR: narration missing or invalid")
        sys.exit(1)

    # ---------------------------
    # 🔒 HARD ALIGNMENT CHECK
    # ---------------------------
    slide_ids = [s["slide_id"] for s in slides]
    narration_ids = [n.get("slide_id") for n in narration]

    if narration_ids != slide_ids:
        print("ERROR: narration slide_id mismatch")
        print("Slides:   ", slide_ids)
        print("Narration:", narration_ids)
        sys.exit(1)

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
