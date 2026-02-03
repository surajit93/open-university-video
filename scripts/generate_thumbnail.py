# scripts/generate_thumbnail.py
# Purpose: Generate a clean, Coursera-style YouTube thumbnail
# Inputs:
# - current_topic.json
# - channel.json (optional)
# Output:
# - thumbnail.png

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# =========================
# FILES
# =========================

TOPIC_FILE = Path("current_topic.json")
CHANNEL_META_FILE = Path("channel.json")
OUT_FILE = Path("thumbnail.png")

# =========================
# CANVAS
# =========================

W, H = 1280, 720
BG_COLOR = "#1e3a8a"   # deep academic blue
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#fde047"  # subtle yellow accent

# =========================
# FONT LOADER
# =========================

def load_font(size, bold=True):
    try:
        if bold:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

# =========================
# AUTO-FIT TEXT
# =========================

def fit_text(draw, text, max_w, max_h, max_size=110, min_size=36):
    for size in range(max_size, min_size, -2):
        font = load_font(size, bold=True)
        lines, line = [], ""

        for word in text.split():
            test = line + word + " "
            if draw.textlength(test, font=font) <= max_w:
                line = test
            else:
                lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())

        total_h = len(lines) * (size + 12)
        if total_h <= max_h:
            return font, lines

    return load_font(min_size, bold=True), [text]

# =========================
# MAIN
# =========================

def main():
    assert TOPIC_FILE.exists(), "current_topic.json missing"

    topic = json.loads(TOPIC_FILE.read_text(encoding="utf-8"))
    title = topic["title"]

    channel_name = "Open Media University"
    if CHANNEL_META_FILE.exists():
        meta = json.loads(CHANNEL_META_FILE.read_text(encoding="utf-8"))
        channel_name = meta.get("channel_name", channel_name)

    img = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(img)

    # -------------------------
    # TITLE (CENTER)
    # -------------------------

    font, lines = fit_text(
        d,
        title,
        max_w=W - 160,
        max_h=H - 260
    )

    y = (H - len(lines) * (font.size + 14)) // 2 - 40
    for line in lines:
        w = d.textlength(line, font=font)
        d.text(((W - w) // 2, y), line, font=font, fill=TEXT_COLOR)
        y += font.size + 14

    # -------------------------
    # FOOTER STRIP
    # -------------------------

    d.rectangle([0, H - 90, W, H], fill="#020617")
    footer_font = load_font(36, bold=False)
    footer_text = f"Full lecture • {channel_name}"

    d.text(
        (40, H - 65),
        footer_text,
        font=footer_font,
        fill=ACCENT_COLOR
    )

    img.save(OUT_FILE)
    print("✔ thumbnail.png generated")

if __name__ == "__main__":
    main()
