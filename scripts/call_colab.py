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

    # Deterministic language
    os.environ["RENDER_LANG"] = RENDER_LANG

    # Coqui + espeak
    # Coqui + espeak
    os.environ["PHONEMIZER_ESPEAK_PATH"] = "/usr/bin/espeak"
    os.environ["ESPEAK_PATH"] = "/usr/bin/espeak"

    # Hard-disable GPU + thread storms (BIG slowdown fix)
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

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
            "--log-output",
            "--progress-bar",
            "--request-save-on-cell-execute",
        ],
        cwd=str(BASE_DIR),
        check=True,
    )

    print("✔ Notebook executed successfully")
    print("✔ Video artifacts generated")

if __name__ == "__main__":
    main()
