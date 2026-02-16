# render/scene_composer.py

from typing import Dict, List
import hashlib
import json
import os
import pickle


class SceneComposer:

    CACHE_DIR = "render/frame_cache"

    def __init__(self):
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def compose_scene(self, scene_data: Dict) -> Dict:
        """
        scene_data:
        {
            "background": "bg_image.png",
            "headline": "AI Just Changed Everything",
            "subtext": "...",
            "accent_element": "circle_glow",
            "duration": 8
        }
        """

        cache_key = self._generate_cache_key(scene_data)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached

        layout = {
            "background_layer": scene_data["background"],
            "midground_graphic": self._inject_midground(scene_data),
            "foreground_text": self._layout_text(scene_data),
            "accent_motion_object": scene_data.get("accent_element", "default_glow"),
            "min_active_elements": 2
        }

        self._validate_scene(layout)

        self._store_in_cache(cache_key, layout)

        return layout

    def _inject_midground(self, scene_data):
        return {
            "type": "overlay_shape",
            "opacity": 0.4
        }

    def _layout_text(self, scene_data):
        return {
            "headline": scene_data["headline"],
            "subtext": scene_data.get("subtext"),
            "position": "safe_zone_center"
        }

    def _validate_scene(self, layout):
        active_layers = [
            layout["background_layer"],
            layout["midground_graphic"],
            layout["foreground_text"],
            layout["accent_motion_object"]
        ]

        if len([x for x in active_layers if x]) < 2:
            raise ValueError("Scene rejected: Not enough active visual elements.")

    # ----------------------------
    # 🔥 NEW: FRAME CACHE ENGINE
    # ----------------------------

    def _generate_cache_key(self, scene_data: Dict) -> str:
        serialized = json.dumps(scene_data, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.CACHE_DIR, f"{key}.pkl")

    def _store_in_cache(self, key: str, layout: Dict):
        with open(self._cache_path(key), "wb") as f:
            pickle.dump(layout, f)

    def _load_from_cache(self, key: str):
        path = self._cache_path(key)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        return None
