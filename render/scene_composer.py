# render/scene_composer.py

from typing import Dict, List


class SceneComposer:

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

        layout = {
            "background_layer": scene_data["background"],
            "midground_graphic": self._inject_midground(scene_data),
            "foreground_text": self._layout_text(scene_data),
            "accent_motion_object": scene_data.get("accent_element", "default_glow"),
            "min_active_elements": 2
        }

        self._validate_scene(layout)

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
