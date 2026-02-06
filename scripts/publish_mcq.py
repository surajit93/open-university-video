# scripts/publish_mcq.py
# PURPOSE:
# - Commit generated MCQ HTML into open-university-mcq repo
# - Push to GitHub
# - Output public GitHub Pages URL for YouTube description

import json
import subprocess
import sys
from pathlib import Path

# =========================
# CONFIG
# =========================

MCQ_REPO_ROOT = Path("open-university-mcq")
MCQ_TESTS_DIR = MCQ_REPO_ROOT / "tests"

CURRENT_TOPIC_FILE = Path("current_topic.json")
MCQ_LINK_FILE = Path("mcq_link.txt")

GITHUB_PAGES_BASE = "https://surajit93.github.io/open-university-mcq/tests"
TARGET_BRANCH = "main"

# =========================
# UTILS
# =========================

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)

# =========================
# MAIN
# =========================

def main():
    if not MCQ_REPO_ROOT.exists():
        print("ERROR: open-university-mcq repo not found")
        sys.exit(1)

    if not CURRENT_TOPIC_FILE.exists():
        print("ERROR: current_topic.json missing")
        sys.exit(1)

    topic = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    topic_id = topic["id"]

    html_file = MCQ_TESTS_DIR / f"{topic_id}.html"

    if not html_file.exists():
        print(f"ERROR: MCQ HTML not found: {html_file}")
        sys.exit(1)

    print("Publishing MCQ to GitHub Pages...")

    # -------------------------
    # 🔒 ENSURE BRANCH (CRITICAL)
    # -------------------------
    run(["git", "fetch", "origin"], cwd=MCQ_REPO_ROOT)
    run(["git", "checkout", TARGET_BRANCH], cwd=MCQ_REPO_ROOT)
    run(["git", "pull", "origin", TARGET_BRANCH], cwd=MCQ_REPO_ROOT)

    # -------------------------
    # COMMIT
    # -------------------------
    run(["git", "status", "--short"], cwd=MCQ_REPO_ROOT)
    run(["git", "add", "tests"], cwd=MCQ_REPO_ROOT)

    commit_msg = f"Add MCQ test for topic {topic_id}"
    run(["git", "commit", "-m", commit_msg], cwd=MCQ_REPO_ROOT)

    # -------------------------
    # PUSH
    # -------------------------
    run(["git", "push", "origin", TARGET_BRANCH], cwd=MCQ_REPO_ROOT)

    # -------------------------
    # PUBLIC URL
    # -------------------------
    mcq_url = f"{GITHUB_PAGES_BASE}/{topic_id}.html"
    MCQ_LINK_FILE.write_text(mcq_url, encoding="utf-8")

    print("✔ MCQ published")
    print("✔ URL:", mcq_url)

if __name__ == "__main__":
    main()
