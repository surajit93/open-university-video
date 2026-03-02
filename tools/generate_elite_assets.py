import numpy as np
import soundfile as sf
from moviepy.editor import VideoClip
from pathlib import Path
from scipy.signal import butter, lfilter
import random
import json

BASE_DIR = Path("assets")
SR = 48000
WIDTH = 1920
HEIGHT = 1080


# ==========================================================
# DIRECTORY SETUP
# ==========================================================

def create_dirs():
    dirs = [
        "overlays",
        "sfx",
        "transitions",
        "grain",
        "light_fx",
        "motion_templates",
        "stock_cache",
        "ai_cache",
    ]
    for d in dirs:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)


# ==========================================================
# AUDIO ENGINE (ELITE)
# ==========================================================

def normalize(audio):
    peak = np.max(np.abs(audio))
    return audio / (peak + 1e-8) * 0.95


def stereo_width(signal, width=0.5):
    left = signal
    right = np.roll(signal, int(500 * width))
    return np.column_stack([left, right])


def multi_band_impact(filename):
    duration = 1.2
    t = np.linspace(0, duration, int(SR * duration))

    sub = np.sin(2 * np.pi * 40 * t) * np.exp(-3 * t)
    mid = np.sin(2 * np.pi * 120 * t) * np.exp(-5 * t)
    high = np.random.randn(len(t)) * np.exp(-30 * t)

    composite = sub + mid + high * 0.4
    composite = normalize(composite)

    sf.write(BASE_DIR / "sfx" / filename,
             stereo_width(composite, 0.6),
             SR)


def harmonic_riser(filename):
    duration = 4.0
    t = np.linspace(0, duration, int(SR * duration))

    base = np.sin(2 * np.pi * (100 + 1500 * t) * t)
    harmonic = np.sin(2 * np.pi * (300 + 2500 * t) * t)
    noise = np.random.randn(len(t)) * 0.2

    envelope = np.linspace(0, 1, len(t)) ** 2

    mix = (base + harmonic * 0.5 + noise) * envelope
    mix = normalize(mix)

    sf.write(BASE_DIR / "sfx" / filename,
             stereo_width(mix, 0.7),
             SR)


def cinematic_whoosh(filename):
    duration = 1.5
    t = np.linspace(0, duration, int(SR * duration))

    noise = np.random.randn(len(t))
    envelope = np.linspace(0, 1, len(t)) ** 3
    filtered = lfilter(*butter(4, 0.4), noise)

    mix = filtered * envelope
    mix = normalize(mix)

    sf.write(BASE_DIR / "sfx" / filename,
             stereo_width(mix, 0.5),
             SR)


# ==========================================================
# VISUAL ENGINE (ELITE)
# ==========================================================

def volumetric_light_leak(filename, seed):
    random.seed(seed)

    def make_frame(t):
        frame = np.zeros((HEIGHT, WIDTH, 3))

        cx = int(WIDTH * (0.3 + 0.4 * np.sin(t * 0.5)))
        cy = int(HEIGHT * (0.5 + 0.3 * np.cos(t * 0.4)))

        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                glow = np.exp(-dist / 250)
                flicker = 0.7 + 0.3 * np.sin(t * 10)
                val = glow * 255 * flicker
                frame[y, x] = [val, val * 0.6, val * 0.3]

        return np.clip(frame, 0, 255).astype(np.uint8)

    clip = VideoClip(make_frame, duration=5)
    clip.write_videofile(
        str(BASE_DIR / "overlays" / filename),
        fps=30,
        codec="libx264",
        audio=False,
        bitrate="8000k"
    )
    clip.close()


def cinematic_glitch(filename):
    def make_frame(t):
        base = np.random.randint(0, 255, (HEIGHT, WIDTH, 3))

        for _ in range(5):
            x_shift = random.randint(-50, 50)
            y_shift = random.randint(-50, 50)
            channel = random.randint(0, 2)
            base[:, :, channel] = np.roll(base[:, :, channel], x_shift, axis=1)
            base[:, :, channel] = np.roll(base[:, :, channel], y_shift, axis=0)

        return base.astype(np.uint8)

    clip = VideoClip(make_frame, duration=2)
    clip.write_videofile(
        str(BASE_DIR / "overlays" / filename),
        fps=30,
        codec="libx264",
        audio=False,
        bitrate="8000k"
    )
    clip.close()


def seamless_grain_loop(filename):
    def make_frame(t):
        noise = np.random.randint(0, 50, (HEIGHT, WIDTH))
        frame = np.stack([noise]*3, axis=-1)
        return frame.astype(np.uint8)

    clip = VideoClip(make_frame, duration=3)
    clip.write_videofile(
        str(BASE_DIR / "grain" / filename),
        fps=30,
        codec="libx264",
        audio=False,
        bitrate="6000k"
    )
    clip.close()


# ==========================================================
# MOTION TEMPLATE GENERATOR
# ==========================================================

def generate_motion_templates():
    templates = {
        "hook_motion": {"zoom": 0.18, "rotation": 1.2, "shake": 0.6},
        "tension_motion": {"zoom": 0.08, "rotation": 0.3, "shake": 0.1},
        "climax_motion": {"zoom": 0.25, "rotation": 2.0, "shake": 0.8},
        "reset_motion": {"zoom": 0.12, "rotation": 0.5, "shake": 0.2}
    }

    for name, data in templates.items():
        with open(BASE_DIR / "motion_templates" / f"{name}.json", "w") as f:
            json.dump(data, f, indent=2)


# ==========================================================
# MAIN
# ==========================================================

def main():
    create_dirs()

    # Generate multiple variants
    for i in range(3):
        volumetric_light_leak(f"light_leak_variant_{i}.mp4", seed=i)
        cinematic_glitch(f"glitch_variant_{i}.mp4")

    seamless_grain_loop("grain_loop.mp4")

    multi_band_impact("impact_pro.wav")
    harmonic_riser("riser_pro.wav")
    cinematic_whoosh("whoosh_pro.wav")

    generate_motion_templates()

    print("ELITE cinematic assets generated.")


if __name__ == "__main__":
    main()
