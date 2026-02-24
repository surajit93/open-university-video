# scripts/generate_storyboard.py
# PURPOSE:
# Generate structured storyboard.json (intent-driven scene abstraction layer)

import json
import os
import sys
from pathlib import Path
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent.parent

TOPIC_FILE = BASE_DIR / "current_topic.json"
OUTPUT_FILE = BASE_DIR / "storyboard.json"

MODEL = "llama3-70b-8192"

SYSTEM_PROMPT = """
You are a high-retention YouTube cinematic storyboard strategist.

Your mission:
Create an intent-driven storyboard designed for maximum viewer retention and psychological engagement.

CRITICAL OBJECTIVES:
- Strong hook in first 3 seconds
- Escalating tension curve
- Emotional pacing (tension → pressure → impact → relief → curiosity)
- Pattern interrupts every 4–8 seconds
- Clear payoff moment
- Visual dominance over text

IMPORTANT:
This is NOT a slide deck.
This is a cinematic execution blueprint.

Output STRICT valid JSON only.
No commentary.
No markdown.

STRUCTURE:

{
  "meta": {
    "style": "challenge",
    "aspect_ratio": "16:9",
    "brand": "Open Media University",
    "retention_strategy": "escalating_tension"
  },
  "scenes": [
    {
      "id": 1,
      "type": "hook",
      "emotion": "shock",
      "duration": 3,
      "template": "challenge_intro",
      "primary_visual_focus": "large centered headline",
      "layers": [
        {"role": "background", "style": "dark minimal tension"},
        {"role": "headline", "text": "..."},
        {"role": "subheadline", "text": "..."}
      ]
    }
  ]
}

REQUIREMENTS:

1. Total video length MUST be between 45 and 60 seconds.
2. First scene MUST be under 4 seconds.
3. At least one countdown scene.
4. At least one high-impact reveal.
5. At least one psychological insight.
6. Final scene must create curiosity.

Each scene MUST define:
- id
- type
- emotion
- duration
- template
- primary_visual_focus
- layers (array)

Allowed scene types:
- hook
- challenge
- countdown
- reveal
- insight
- pattern_interrupt
- call_to_action

Allowed templates:
- challenge_intro
- countdown_scene
- reveal_flash
- insight_focus
- rapid_zoom_interrupt
- end_card

Layer roles allowed:
- background
- headline
- subheadline
- countdown_timer
- kinetic_text
- infographic
- symbol
- motion_element

Design scenes visually first, text second.
Assume camera movement and motion will be applied.
"""


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_topic():
    if not TOPIC_FILE.exists():
        fail("current_topic.json not found")

    return json.loads(TOPIC_FILE.read_text())


def call_llm(topic_text):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        fail("GROQ_API_KEY missing")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": topic_text}
        ]
    )

    return response.choices[0].message.content


def validate_storyboard(data):
    if "scenes" not in data:
        fail("Storyboard missing scenes")

    if not isinstance(data["scenes"], list):
        fail("Scenes must be a list")

    total_duration = 0

    for scene in data["scenes"]:
        required = [
            "id",
            "type",
            "emotion",
            "duration",
            "template",
            "primary_visual_focus",
            "layers"
        ]

        for r in required:
            if r not in scene:
                fail(f"Scene missing field: {r}")

        if not isinstance(scene["layers"], list):
            fail("Scene layers must be a list")

        total_duration += scene["duration"]

    if total_duration < 45 or total_duration > 60:
        fail("Storyboard duration must be between 45 and 60 seconds")

    if data["scenes"][0]["duration"] >= 4:
        fail("First scene must be under 4 seconds")

    return True


def main():
    print("✔ Loading topic...")
    topic_data = load_topic()

    topic_text = topic_data.get("topic")
    if not topic_text:
        fail("Topic missing in current_topic.json")

    print("✔ Generating storyboard via LLM...")
    raw_output = call_llm(topic_text)

    try:
        storyboard = json.loads(raw_output)
    except Exception:
        fail("LLM did not return valid JSON")

    print("✔ Validating storyboard structure...")
    validate_storyboard(storyboard)

    OUTPUT_FILE.write_text(json.dumps(storyboard, indent=2))

    print("✔ storyboard.json generated successfully")


if __name__ == "__main__":
    main()
