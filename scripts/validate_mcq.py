import json
import sys
from pathlib import Path

MCQ_FILE = Path("mcq.json")
REQUIRED_QUESTIONS = 10
REQUIRED_OPTIONS = 4


def fail(msg: str):
    print(f"VALIDATION ERROR: {msg}")
    sys.exit(1)


def main():
    if not MCQ_FILE.exists():
        fail("mcq.json not found")

    try:
        data = json.loads(MCQ_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        fail("mcq.json is not valid JSON")

    # Top-level keys
    for key in ["topic_id", "title", "questions"]:
        if key not in data:
            fail(f"Missing top-level key: {key}")

    questions = data["questions"]

    if not isinstance(questions, list):
        fail("questions must be a list")

    if len(questions) != REQUIRED_QUESTIONS:
        fail(f"Expected {REQUIRED_QUESTIONS} questions, got {len(questions)}")

    for idx, q in enumerate(questions):
        if not isinstance(q, dict):
            fail(f"Question {idx} is not an object")

        for key in ["q", "options", "answer", "explanation"]:
            if key not in q:
                fail(f"Question {idx} missing key: {key}")

        if not isinstance(q["q"], str) or not q["q"].strip():
            fail(f"Question {idx} text invalid")

        options = q["options"]
        if not isinstance(options, list) or len(options) != REQUIRED_OPTIONS:
            fail(f"Question {idx} must have exactly {REQUIRED_OPTIONS} options")

        for opt_i, opt in enumerate(options):
            if not isinstance(opt, str) or not opt.strip():
                fail(f"Question {idx} option {opt_i} invalid")

        answer = q["answer"]
        if not isinstance(answer, int):
            fail(f"Question {idx} answer must be integer")

        if answer < 0 or answer >= REQUIRED_OPTIONS:
            fail(f"Question {idx} answer index out of range")

        if not isinstance(q["explanation"], str) or not q["explanation"].strip():
            fail(f"Question {idx} explanation invalid")

    print("MCQ validation passed")


if __name__ == "__main__":
    main()

