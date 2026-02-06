# scripts/publish_mcq.py
# PURPOSE:
# - Commit generated MCQ HTML into open-university-mcq repo
# - Push to GitHub using PAT (MCQ_PUSH_TOKEN)
# - Output public GitHub Pages URL

import json
import subprocess
import sys
import os
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

MCQ_PUSH_TOKEN = os.environ.get("MCQ_PUSH_TOKEN")


# =========================
# UTILS
# =========================

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


# =========================
# MAIN
# =========================

def main():
    # -------------------------
    # HARD FAILS
    # -------------------------

    if not MCQ_PUSH_TOKEN:
        print("ERROR: MCQ_PUSH_TOKEN missing")
        sys.exit(1)

    if not MCQ_REPO_ROOT.exists():
        print("ERROR: open-university-mcq repo not found")
        sys.exit(1)

    if not CURRENT_TOPIC_FILE.exists():
        print("ERROR: current_topic.json missing")
        sys.exit(1)

    # -------------------------
    # LOAD TOPIC
    # -------------------------

    topic = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    topic_id = topic["id"]

    html_file = MCQ_TESTS_DIR / f"{topic_id}.html"
    if not html_file.exists():
        print(f"ERROR: MCQ HTML not found: {html_file}")
        sys.exit(1)

    print("Publishing MCQ to GitHub Pages...")

    # -------------------------
    # GIT SETUP (CI SAFE)
    # -------------------------

    # Ensure correct branch
    run(["git", "checkout", TARGET_BRANCH], cwd=MCQ_REPO_ROOT)

    # Identity REQUIRED in GitHub Actions
    run(["git", "config", "user.email", "ci@open-university"], cwd=MCQ_REPO_ROOT)
    run(["git", "config", "user.name", "Open University CI"], cwd=MCQ_REPO_ROOT)

    # Inject PAT into origin
    auth_repo_url = (
        f"https://x-access-token:{MCQ_PUSH_TOKEN}"
        f"@github.com/surajit93/open-university-mcq.git"
    )
    run(["git", "remote", "set-url", "origin", auth_repo_url], cwd=MCQ_REPO_ROOT)

    # -------------------------
    # COMMIT + PUSH
    # -------------------------

    run(["git", "add", "tests"], cwd=MCQ_REPO_ROOT)

    # Commit may fail if nothing changed – handle cleanly
    try:
        run(
            ["git", "commit", "-m", f"Add MCQ test for topic {topic_id}"],
            cwd=MCQ_REPO_ROOT,
        )
    except subprocess.CalledProcessError:
        print("ℹ️  No new MCQ changes to commit")

    run(["git", "push", "origin", TARGET_BRANCH], cwd=MCQ_REPO_ROOT)

    # -------------------------
    # WRITE PUBLIC URL
    # -------------------------

    mcq_url = f"{GITHUB_PAGES_BASE}/{topic_id}.html"
    MCQ_LINK_FILE.write_text(mcq_url, encoding="utf-8")

    print("✔ MCQ published")
    print("✔ URL:", mcq_url)


if __name__ == "__main__":
    main()
