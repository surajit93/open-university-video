import sys
import json
import re
from pathlib import Path

# ============================
# CONFIG
# ============================

MCQ_REPO_ROOT = Path("open-university-mcq")
MCQ_TESTS_DIR = MCQ_REPO_ROOT / "tests"

REQUIRED_QUESTIONS = 10
REQUIRED_OPTIONS = 4


def fail(msg: str):
    print(f"VALIDATION ERROR: {msg}")
    sys.exit(1)


def extract_questions(html: str):
    """
    Extracts the QUESTIONS JS array from HTML.
    """
    match = re.search(
        r"const QUESTIONS\s*=\s*(\[[\s\S]*?\]);",
        html
    )
    if not match:
        fail("QUESTIONS array not found in MCQ HTML")

    raw = match.group(1)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"QUESTIONS JSON invalid: {e}")


def main():
    if not MCQ_REPO_ROOT.exists():
        fail("open-university-mcq repo not found")

    if not MCQ_TESTS_DIR.exists():
        fail("tests directory not found in MCQ repo")

    html_files = sorted(MCQ_TESTS_DIR.glob("*.html"))

    if not html_files:
        fail("No MCQ HTML files found in tests/")

    mcq_file = html_files[-1]
    html = mcq_file.read_text(encoding="utf-8")

    questions = extract_questions(html)

    # ----------------------------
    # Question count
    # ----------------------------
    if not isinstance(questions, list):
        fail("QUESTIONS is not a list")

    if len(questions) != REQUIRED_QUESTIONS:
        fail(
            f"Expected {REQUIRED_QUESTIONS} questions, "
            f"found {len(questions)} in {mcq_file.name}"
        )

    # ----------------------------
    # Per-question validation
    # ----------------------------
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            fail(f"Question {i} is not an object")

        for key in ["q", "options", "answer"]:
            if key not in q:
                fail(f"Question {i} missing key: {key}")

        if not isinstance(q["options"], list):
            fail(f"Question {i} options not a list")

        if len(q["options"]) != REQUIRED_OPTIONS:
            fail(
                f"Question {i} expected {REQUIRED_OPTIONS} options, "
                f"found {len(q['options'])}"
            )

        if not isinstance(q["answer"], int):
            fail(f"Question {i} answer is not an integer")

        if q["answer"] < 0 or q["answer"] >= REQUIRED_OPTIONS:
            fail(f"Question {i} answer index out of range")

    print(f"✔ MCQ validation passed ({mcq_file.name})")


if __name__ == "__main__":
    main()
