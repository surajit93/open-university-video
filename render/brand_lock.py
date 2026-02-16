# render/brand_lock.py

from typing import Dict
import yaml


def load_channel_config():
    with open("config/channel_config.yaml", "r") as f:
        return yaml.safe_load(f)


class BrandLock:

    def __init__(self, config: Dict = None):
        if config is None:
            config = load_channel_config()

        self.font = config.get("font_family")
        self.accent = config.get("accent_color")
        self.animation_curve = config.get("animation_curve")

    def apply_brand(self, scene: Dict) -> Dict:
        scene["brand"] = {
            "font_family": self.font,
            "accent_color": self.accent,
            "animation_curve": self.animation_curve,
            "watermark": {
                "opacity": 0.3,
                "duration": "full"
            },
            "intro_micro_sting": {
                "duration_seconds": 0.8
            }
        }
        return scene
