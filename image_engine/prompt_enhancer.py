"""
prompt_enhancer.py
Enhances scene concept into cinematic image prompt.
"""

import json
from pathlib import Path


class PromptEnhancer:

    def __init__(self, style_config_path="image_engine/style_profiles.json"):
        with open(style_config_path, "r", encoding="utf-8") as f:
            self.styles = json.load(f)

    def enhance(self, concept: str, style_profile: str) -> str:

        style = self.styles.get(style_profile, {})

        lighting = style.get("lighting", "")
        palette = style.get("color_palette", "")
        mood = style.get("mood", "")
        camera = style.get("camera", "")

        enhanced_prompt = (
            f"{concept}, {lighting}, {palette}, "
            f"{mood}, {camera}, ultra detailed, 8k resolution, cinematic quality"
        )

        return enhanced_prompt
