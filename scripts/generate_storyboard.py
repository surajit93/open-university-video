# scripts/generate_storyboard.py
# PURPOSE:
# Generate structured storyboard.json (scene-based abstraction layer)

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
You are a high-retention YouTube storyboard strategist designing a Bright Side level video.

Your mission:
Create a cinematic, tension-driven storyboard designed to maximize viewer retention and psychological engagement.

CRITICAL OBJECTIVES:
- Strong hook in first 3 seconds
- Escalating challenge structure
- Emotional pacing curve (tension → pressure → impact → relief → curiosity)
- Frequent pattern interrupts (every 4–8 seconds)
- Clear reward payoff moment
- High visual dominance over text

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
      "headline": "...",
      "subheadline": "...",
      "template": "challenge_intro"
    }
  ]
}

REQUIREMENTS:

1. Total video length: 45–60 seconds.
2. First scene MUST be under 4 seconds.
3. At least one countdown-driven challenge scene.
4. At least one high-impact reveal scene.
5. At least one psychological insight scene.
6. Final scene must create curiosity for next episode.

Scene Types Allowed:
- hook
- challenge
- countdown
- reveal
- insight
- pattern_interrupt
- call_to_action

Templates Allowed:
- challenge_intro
- countdown_scene
- reveal_flash
- insight_focus
- rapid_zoom_interrupt
- end_card

Design scenes visually first, text second.
Assume strong motion, camera movement, and sound hits will be applied.

Each scene must define:
- id
- type
- emotion
- duration
- template
- primary_visual_focus (what dominates frame)
"""


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_topic():
    if not TOPIC_FILE.exists():
        fail("current_topic.json not found")

    return json.loads(TOPIC_FILE.read_text())


def call_llm(topic_text):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    if not client:
        fail("GROQ_API_KEY missing")

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
        required = ["id", "type", "emotion", "duration", "template"]
        for r in required:
            if r not in scene:
                fail(f"Scene missing field: {r}")

        total_duration += scene["duration"]

    if total_duration < 30:
        fail("Storyboard too short (<30s)")

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
