import json, os, sys
from pathlib import Path
from groq import Groq

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL = "llama-3.1-8b-instant"

CURRENT_TOPIC_FILE = Path("current_topic.json")
SLIDE_PLAN_FILE = Path("slide_plan.json")

client = Groq(api_key=GROQ_API_KEY)

def main():
    topic = json.loads(CURRENT_TOPIC_FILE.read_text())

    prompt = f"""
Return ONLY valid JSON.

Create slides for a university lecture.

Title: {topic["title"]}
Outline: {topic.get("outline","")}
Expected duration: {topic.get("expected_duration_min",8)} minutes

STRICT FORMAT:
{{
  "slides": [
    {{
      "slide_id": 1,
      "title": "",
      "visual_strategy": "CONCEPT_DIAGRAM | FLOW_DIAGRAM | SYSTEM_DIAGRAM | TEXT_ONLY",
      "left_panel_plan": {{
        "diagram_boxes": [],
        "description": ""
      }},
      "right_panel_gist": ""
    }}
  ]
}}

No markdown. No prose. No narration.
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.3,
        max_tokens=3000,
    )

    data = json.loads(resp.choices[0].message.content)
    SLIDE_PLAN_FILE.write_text(json.dumps(data, indent=2))
    print("✔ slide_plan.json written")

if __name__ == "__main__":
    main()
