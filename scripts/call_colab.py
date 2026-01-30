# scripts/call_colab.py
# ONE PURPOSE: execute the Colab notebook non-interactively using generated files
# Assumes:
# - slide_plan.json
# - script.txt
# - slide_audio_map.json
# already exist in project root
# - notebook file name is video_pipeline.ipynb

import sys
import subprocess
from pathlib import Path

# Notebook is stored OUTSIDE scripts/
NOTEBOOK = Path("../open_university_video_renderer.ipynb")

REQUIRED_FILES = [
    Path("slide_plan.json"),
    Path("script.txt"),
    Path("slide_audio_map.json"),
]

OUTPUT_NOTEBOOK = Path("executed_open_university_video_renderer.ipynb")


def main():
    missing = [f.name for f in REQUIRED_FILES if not f.exists()]
    if missing:
        print("ERROR: Missing required files:", ", ".join(missing))
        sys.exit(1)

    if not NOTEBOOK.exists():
        print(f"ERROR: Notebook not found: {NOTEBOOK}")
        sys.exit(1)

    print("Executing Colab notebook via papermill...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "papermill",
            str(NOTEBOOK),
            str(OUTPUT_NOTEBOOK),
            "-p", "SLIDE_PLAN_PATH", "slide_plan.json",
            "-p", "SCRIPT_PATH", "script.txt",
            "-p", "AUDIO_MAP_PATH", "slide_audio_map.json",
        ],
        check=True
    )

    print("Notebook executed successfully")


if __name__ == "__main__":
    main()

