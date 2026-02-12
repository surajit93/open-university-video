# scripts/thumbnail_renderer.py

from PIL import Image, ImageDraw, ImageFont
import os
from scripts.asset_registry import get_asset

WIDTH = 1280
HEIGHT = 720


def auto_scale_font(draw, text, font_path, max_width, max_height):
    size = 150
    while size > 30:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_width and h <= max_height:
            return font

        size -= 5

    return ImageFont.truetype(font_path, 40)


def render_thumbnail(text, bg_color, output_path):
    os.makedirs("outputs/thumbnails", exist_ok=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    font_path = get_asset("font")

    font = auto_scale_font(draw, text, font_path, WIDTH * 0.85, HEIGHT * 0.6)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2

    draw.text((x, y), text, font=font, fill="white")

    img.save(output_path)

    return output_path
