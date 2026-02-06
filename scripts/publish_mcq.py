# scripts/publish_mcq.py

import json
import subprocess
import sys
from pathlib import Path

MCQ_REPO_ROOT = Path("open-university-mcq")
MCQ_TESTS_DIR = MCQ_REPO_ROOT / "tests"

CURRENT_TOPIC_FILE = Path("current_topic.json")
MCQ_LINK_FILE = Path("mcq_link.txt")

GITHUB_PAGES_BASE = "https://surajit93.github.io/open-university-mcq/tests"
TARGET_BRANCH = "main"

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)

def main():
    if not MCQ_REPO_ROOT.exists():
        print("ERROR: open-university-mcq repo not found")
        sys.exit(1)

    topic = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    topic_id = topic["id"]

    html_file = MCQ_TESTS_DIR / f"{topic_id}.html"
    if not html_file.exists():
        print(f"ERROR: MCQ HTML not found: {html_file}")
        sys.exit(1)

    print("Publishing MCQ to GitHub Pages...")

    # Ensure branch
    run(["git", "checkout", TARGET_BRANCH], cwd=MCQ_REPO_ROOT)

    run(["git", "add", "tests"], cwd=MCQ_REPO_ROOT)
    run(["git", "commit", "-m", f"Add MCQ test for topic {topic_id}"], cwd=MCQ_REPO_ROOT)

    # 🔐 AUTHENTICATED PUSH
    run([
        "git", "push",
        f"https://x-access-token:{os.environ['MCQ_PUSH_TOKEN']}@github.com/surajit93/open-university-mcq.git",
        TARGET_BRANCH
    ], cwd=MCQ_REPO_ROOT)

    mcq_url = f"{GITHUB_PAGES_BASE}/{topic_id}.html"
    MCQ_LINK_FILE.write_text(mcq_url, encoding="utf-8")

    print("✔ MCQ published")
    print("✔ URL:", mcq_url)

if __name__ == "__main__":
    import os
    if "MCQ_PUSH_TOKEN" not in os.environ:
        print("ERROR: MCQ_PUSH_TOKEN missing")
        sys.exit(1)
    main()
