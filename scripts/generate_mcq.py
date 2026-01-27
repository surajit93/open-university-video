import json
import os
import sys
import requests
from pathlib import Path

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_TOKEN = os.environ.get("HF_TOKEN")

CURRENT_TOPIC_FILE = Path("current_topic.json")
TRANSCRIPT_FILE = Path("transcript.txt")
MCQ_FILE = Path("mcq.json")

REQUIRED_QUESTIONS = 10


def hf_generate(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1200,
            "temperature": 0.3,
            "top_p": 0.9
        }
    }
    r = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    raise RuntimeError("Unexpected HF response")


def main():
    if not CURRENT_TOPIC_FILE.exists() or not TRANSCRIPT_FILE.exists():
        print("ERROR: required input files missing")
        sys.exit(1)

    topic = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    transcript = TRANSCRIPT_FILE.read_text(encoding="utf-8").strip()

    prompt = f"""
You are generating exam-style multiple choice questions.

INPUT RULES:
- Use ONLY the transcript below
- Do NOT use outside knowledge
- Do NOT assume learner level
- Do NOT invent concepts

OUTPUT RULES (STRICT):
- Output VALID JSON ONLY
- Output MUST match this schema EXACTLY:

{{
  "topic_id": "{topic['id']}",
  "title": "{topic['title']}",
  "questions": [
    {{
      "q": "",
      "options": ["", "", "", ""],
      "answer": 0,
      "explanation": ""
    }}
  ]
}}

QUESTION RULES:
- Generate EXACTLY {REQUIRED_QUESTIONS} questions
- Each question must test a DIFFERENT idea from the transcript
- 4 options per question
- Exactly 1 correct option
- answer = index (0–3)
- No trick questions
- No "all of the above"
- No negative phrasing
- Neutral academic tone
- Explanations must directly reflect transcript content

FAIL CONDITION:
- If transcript is insufficient, output an empty questions array.

TRANSCRIPT:
<<<
{transcript}
>>>
"""

    print("Generating MCQs...")
    raw = hf_generate(prompt)

    try:
        mcq = json.loads(raw)
    except json.JSONDecodeError:
        print("ERROR: model did not return valid JSON")
        sys.exit(1)

    questions = mcq.get("questions", [])
    if len(questions) != REQUIRED_QUESTIONS:
        print(f"ERROR: expected {REQUIRED_QUESTIONS} questions, got {len(questions)}")
        sys.exit(1)

    MCQ_FILE.write_text(json.dumps(mcq, indent=2), encoding="utf-8")
    print("MCQs generated successfully")


if __name__ == "__main__":
    main()

