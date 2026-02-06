# scripts/call_colab.py
# PURPOSE:
# Execute open_university_video_renderer.ipynb non-interactively using Papermill
# Produces executed_open_university_video_renderer.ipynb and final.mp4
#
# This version is CI-safe, deterministic, and dependency-aware.

import os
import sys
import subprocess
from pathlib import Path


# ==============================
# PATH RESOLUTION (ABSOLUTE)
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

NOTEBOOK = BASE_DIR / "open_university_video_renderer.ipynb"
OUTPUT_NOTEBOOK = BASE_DIR / "executed_open_university_video_renderer.ipynb"

SLIDE_PLAN = BASE_DIR / "slide_plan.json"
AUDIO_MAP = BASE_DIR / "slide_audio_map.json"


# ==============================
# PRE-FLIGHT CHECKS
# ==============================

def hard_fail(msg: str):
    print(f"❌ {msg}")
    sys.exit(1)


def check_required_files():
    missing = []
    for f in [NOTEBOOK, SLIDE_PLAN, AUDIO_MAP]:
        if not f.exists():
            missing.append(f.name)

    if missing:
        hard_fail(f"Missing required files: {', '.join(missing)}")


def ensure_papermill():
    try:
        import papermill  # noqa
    except ImportError:
        print("ℹ️  papermill not found, installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "papermill"],
            check=True,
        )


def configure_espeak_env():
    # Required by Coqui TTS phonemizer
    os.environ.setdefault(
        "PHONEMIZER_ESPEAK_PATH",
        "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1",
    )
    os.environ.setdefault(
        "ESPEAK_PATH",
        "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1",
    )


# ==============================
# MAIN EXECUTION
# ==============================

def main():
    print("✔ Verifying renderer inputs...")
    check_required_files()

    print("✔ Ensuring papermill availability...")
    ensure_papermill()

    print("✔ Configuring eSpeak environment...")
    configure_espeak_env()

    print("✔ Executing renderer notebook via papermill...")
    print(f"  Notebook: {NOTEBOOK.name}")
    print(f"  Output:   {OUTPUT_NOTEBOOK.name}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "papermill",
            str(NOTEBOOK),
            str(OUTPUT_NOTEBOOK),
            "-p", "SLIDE_PLAN_PATH", SLIDE_PLAN.name,
            "-p", "AUDIO_MAP_PATH", AUDIO_MAP.name,
        ],
        cwd=str(BASE_DIR),
        check=True,
    )

    print("✔ Notebook executed successfully")

    final_video = BASE_DIR / "final.mp4"
    if not final_video.exists():
        hard_fail("Renderer completed but final.mp4 not found")

    print("✔ final.mp4 generated successfully")


if __name__ == "__main__":
    main()
