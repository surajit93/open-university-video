# scripts/generate_subtitles.py

import json
import sys
from pathlib import Path

import soundfile as sf

# ================================
# FILES
# ================================

AUDIO_MAP_FILE = Path("slide_audio_map.json")
OUT_FILE = Path("final.srt")

# ================================
# HELPERS
# ================================

def ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def wav_duration(path: Path) -> float:
    if not path.exists():
        raise FileNotFoundError(f"Missing audio file: {path}")
    with sf.SoundFile(path) as f:
        return len(f) / f.samplerate

# ================================
# MAIN
# ================================

def main():
    if not AUDIO_MAP_FILE.exists():
        print("ERROR: slide_audio_map.json not found")
        sys.exit(1)

    audio_map = json.loads(AUDIO_MAP_FILE.read_text(encoding="utf-8"))

    lines = []
    cursor = 0.0
    idx = 1

    for item in audio_map:
        slide_id = item["slide_id"]
        text = item["spoken_text"].strip()

        if not text:
            raise ValueError(f"Empty spoken_text for slide {slide_id}")

        wav = Path(f"voice_final_{slide_id}.wav")
        dur = wav_duration(wav)

        start = cursor
        end = cursor + dur

        lines.extend([
            str(idx),
            f"{ts(start)} --> {ts(end)}",
            text,
            ""
        ])

        cursor = end
        idx += 1

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"✔ Subtitles written: {OUT_FILE}")

if __name__ == "__main__":
    main()
