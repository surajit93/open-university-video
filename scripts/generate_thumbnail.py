# scripts/generate_thumbnail.py
# Purpose: Generate a clean, high-CTR YouTube thumbnail
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

# Default fallback colors (UNCHANGED BASE)
BG_COLOR = "#1e3a8a"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#fde047"

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
# 🔥 COLOR STRATEGY ENGINE (ADDITIVE)
# =========================

def apply_color_strategy(strategy_name):
    strategy = (strategy_name or "").lower()

    if "red" in strategy and "black" in strategy:
        return "#0f0f0f", "#ffffff", "#ff0000"

    if "yellow" in strategy and "blue" in strategy:
        return "#0b3c91", "#ffffff", "#ffd400"

    if "cyan" in strategy:
        return "#0b0f1a", "#ffffff", "#00eaff"

    if "face" in strategy:
        return "#111111", "#ffffff", "#ffcc00"

    # fallback
    return BG_COLOR, TEXT_COLOR, ACCENT_COLOR

# =========================
# MAIN
# =========================

def main():
    assert TOPIC_FILE.exists(), "current_topic.json missing"

    topic = json.loads(TOPIC_FILE.read_text(encoding="utf-8"))

    title = topic.get("title", "")
    thumb_text = topic.get("thumbnail_text", "")
    color_strategy = topic.get("thumbnail_color_strategy", "")
    retention_type = topic.get("retention_type", "psychological")
    addiction_score = topic.get("addiction_score", 0.5)

    # Apply dynamic color strategy
    bg_color, text_color, accent_color = apply_color_strategy(color_strategy)

    channel_name = "Open Media University"
    if CHANNEL_META_FILE.exists():
        meta = json.loads(CHANNEL_META_FILE.read_text(encoding="utf-8"))
        channel_name = meta.get("channel_name", channel_name)

    img = Image.new("RGB", (W, H), bg_color)
    d = ImageDraw.Draw(img)

    # -------------------------
    # 🔥 BIG TOP TEXT (thumbnail_text)
    # -------------------------

    if thumb_text:
        badge_font = load_font(120, bold=True)

        text_w = d.textlength(thumb_text, font=badge_font)

        # Background badge
        padding = 40
        box_w = text_w + padding * 2
        box_h = 160

        d.rectangle(
            [
                (W - box_w) // 2,
                80,
                (W + box_w) // 2,
                80 + box_h
            ],
            fill=accent_color
        )

        d.text(
            ((W - text_w) // 2, 110),
            thumb_text,
            font=badge_font,
            fill="#000000"
        )

    # -------------------------
    # TITLE (CENTER LOWER AREA)
    # -------------------------

    font, lines = fit_text(
        d,
        title,
        max_w=W - 160,
        max_h=H - 320
    )

    y = 280
    for line in lines:
        w = d.textlength(line, font=font)
        d.text(((W - w) // 2, y), line, font=font, fill=text_color)
        y += font.size + 14

    # -------------------------
    # 🔥 RETENTION BADGE (ADDITIVE)
    # -------------------------

    if retention_type == "game":
        d.rectangle([40, 40, 280, 110], fill="#ff0000")
        badge_font = load_font(40, bold=True)
        d.text((60, 55), "CHALLENGE", font=badge_font, fill="#ffffff")

    if addiction_score > 0.8:
        d.rectangle([W - 300, 40, W - 40, 110], fill="#16a34a")
        score_font = load_font(38, bold=True)
        d.text((W - 285, 55), "HIGH IMPACT", font=score_font, fill="#ffffff")

    # -------------------------
    # FOOTER STRIP (UNCHANGED STRUCTURE)
    # -------------------------

    d.rectangle([0, H - 90, W, H], fill="#020617")
    footer_font = load_font(36, bold=False)
    footer_text = f"{channel_name}"

    d.text(
        (40, H - 65),
        footer_text,
        font=footer_font,
        fill=accent_color
    )

    img.save(OUT_FILE)
    print("✔ thumbnail.png generated")


if __name__ == "__main__":
    main()
