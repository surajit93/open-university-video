# scripts/call_colab.py
# PURPOSE:
# Execute the Open University renderer notebook non-interactively (Papermill)
# Renderer is DUMB and driven ONLY by slide_plan.json + slide_audio_map.json

import sys
import subprocess
from pathlib import Path

# -----------------------------
# PATHS (repo-root relative)
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

NOTEBOOK = BASE_DIR / "open_university_video_renderer.ipynb"
OUTPUT_NOTEBOOK = BASE_DIR / "executed_open_university_video_renderer.ipynb"

REQUIRED_FILES = [
    BASE_DIR / "slide_plan.json",
    BASE_DIR / "slide_audio_map.json",
]

# -----------------------------
# MAIN
# -----------------------------

def main():
    missing = [f.name for f in REQUIRED_FILES if not f.exists()]
    if missing:
        print("ERROR: Missing required files:", ", ".join(missing))
        sys.exit(1)

    if not NOTEBOOK.exists():
        print(f"ERROR: Notebook not found: {NOTEBOOK}")
        sys.exit(1)

    print("Executing renderer notebook via papermill...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "papermill",
            str(NOTEBOOK),
            str(OUTPUT_NOTEBOOK),
            "-p", "SLIDE_PLAN_PATH", "slide_plan.json",
            "-p", "AUDIO_MAP_PATH", "slide_audio_map.json",
        ],
        cwd=str(BASE_DIR),
        check=True,
    )

    print("✔ Notebook executed successfully")
    print("✔ Video artifacts generated")


if __name__ == "__main__":
    main()
