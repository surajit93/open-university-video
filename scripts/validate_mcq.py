import sys
from pathlib import Path
import re

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


def main():
    if not MCQ_REPO_ROOT.exists():
        fail("open-university-mcq repo not found")

    if not MCQ_TESTS_DIR.exists():
        fail("tests directory not found in MCQ repo")

    html_files = sorted(MCQ_TESTS_DIR.glob("*.html"))

    if not html_files:
        fail("No MCQ HTML files found in tests/")

    # Validate the most recent MCQ
    mcq_file = html_files[-1]
    html = mcq_file.read_text(encoding="utf-8")

    # ----------------------------
    # Question count
    # ----------------------------
    questions = re.findall(r'class="question"', html)
    if len(questions) != REQUIRED_QUESTIONS:
        fail(
            f"Expected {REQUIRED_QUESTIONS} questions, "
            f"found {len(questions)} in {mcq_file.name}"
        )

    # ----------------------------
    # Options per question
    # ----------------------------
    option_blocks = re.findall(
        r'<input type="radio" name="q\d+"',
        html
    )

    if len(option_blocks) != REQUIRED_QUESTIONS * REQUIRED_OPTIONS:
        fail(
            f"Expected {REQUIRED_OPTIONS} options per question "
            f"({REQUIRED_QUESTIONS * REQUIRED_OPTIONS} total), "
            f"found {len(option_blocks)}"
        )

    print(f"✔ MCQ validation passed ({mcq_file.name})")


if __name__ == "__main__":
    main()
