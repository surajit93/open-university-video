# scripts/call_colab.py
# PURPOSE:
# Execute the Open University renderer notebook deterministically in CI
# Enforces stable, Coursera-grade rendering (no random TTS failures)

import sys
import subprocess
import os
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
# CONSTANTS
# -----------------------------

# Coursera-style: single guaranteed language
# Multi-language dubbing is a separate concern
RENDER_LANG = "en"

# -----------------------------
# HELPERS
# -----------------------------

def fail(msg: str):
    print(f"ERROR: {msg}")
    sys.exit(1)


# -----------------------------
# MAIN
# -----------------------------

def main():
    print("✔ Verifying renderer inputs...")

    missing = [f.name for f in REQUIRED_FILES if not f.exists()]
    if missing:
        fail(f"Missing required files: {', '.join(missing)}")

    if not NOTEBOOK.exists():
        fail(f"Notebook not found: {NOTEBOOK}")

    print("✔ Ensuring papermill availability...")
    try:
        subprocess.run(
            [sys.executable, "-m", "papermill", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    except Exception:
        fail("papermill is not available in this environment")

    # -----------------------------
    # ENVIRONMENT GUARANTEES
    # -----------------------------

    print("✔ Configuring stable TTS environment...")

    # Force deterministic rendering
    os.environ["RENDER_LANG"] = RENDER_LANG

    # Required for Coqui + espeak
    os.environ["PHONEMIZER_ESPEAK_PATH"] = "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1"
    os.environ["ESPEAK_PATH"] = "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1"

    # Prevent torch from probing GPUs
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # -----------------------------
    # EXECUTION
    # -----------------------------

    print("✔ Executing renderer notebook via papermill...")
    print(f"  Notebook: {NOTEBOOK.name}")
    print(f"  Output:   {OUTPUT_NOTEBOOK.name}")
    print(f"  Language: {RENDER_LANG}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "papermill",
            str(NOTEBOOK),
            str(OUTPUT_NOTEBOOK),
        ],
        cwd=str(BASE_DIR),
        check=True,
    )

    print("✔ Notebook executed successfully")
    print("✔ Video artifacts generated")


if __name__ == "__main__":
    main()
