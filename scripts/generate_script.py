import json
import os
import sys
import requests
from pathlib import Path

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_TOKEN = os.environ.get("HF_TOKEN")

CURRENT_TOPIC_FILE = Path("current_topic.json")
SCRIPT_FILE = Path("script.txt")
TRANSCRIPT_FILE = Path("transcript.txt")

MIN_WORDS = 750    # ~5 minutes
MAX_WORDS = 1400   # ~10 minutes


def hf_generate(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1800,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    r = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    raise RuntimeError("Unexpected HF response")


def clean_transcript(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            continue
        lines.append(line)
    return " ".join(lines)


def main():
    if not CURRENT_TOPIC_FILE.exists():
        print("ERROR: current_topic.json not found")
        sys.exit(1)

    with CURRENT_TOPIC_FILE.open("r", encoding="utf-8") as f:
        topic = json.load(f)

    title = topic["title"]

    prompt = f"""
You are writing a university lecture narration.

Topic title:
{title}

Rules:
- Write as spoken academic English
- Calm, confident, human tone
- Short sentences
- Natural pauses
- No hype
- No self reference
- No phrases like "in this video"
- No bullet lists
- No emojis
- No AI disclaimers

Structure:
1. Start with a real-world problem or question
2. Explain core ideas step by step
3. Use simple examples
4. Explain why this matters
5. End with a reflective closing thought

Insert occasional pacing markers like:
[PAUSE]
[SHIFT]

Target length:
Between {MIN_WORDS} and {MAX_WORDS} words.
"""

    print("Generating lecture script...")
    script = hf_generate(prompt)

    words = script.split()
    if len(words) < MIN_WORDS or len(words) > MAX_WORDS:
        print(f"ERROR: Script length {len(words)} words out of bounds")
        sys.exit(1)

    transcript = clean_transcript(script)

    SCRIPT_FILE.write_text(script, encoding="utf-8")
    TRANSCRIPT_FILE.write_text(transcript, encoding="utf-8")

    print(f"Script generated for topic: {title}")
    print(f"Word count: {len(words)}")


if __name__ == "__main__":
    main()

