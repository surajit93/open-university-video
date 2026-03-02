"""
arc_designer.py
Implements multi-arc tension strategy for 8–12 min videos.
"""

from typing import List
from scene_engine.scene_schema import Scene


class ArcDesigner:

    def apply_multi_arc_structure(self, scenes: List[Scene]) -> List[Scene]:
        total = len(scenes)

        for idx, scene in enumerate(scenes):
            progress = idx / total

            if progress < 0.1:
                scene.scene_type = "hook"
                scene.audio.bg_curve = "intense"
            elif progress < 0.5:
                scene.scene_type = "tension"
                scene.audio.bg_curve = "rising"
            elif progress < 0.85:
                scene.scene_type = "explanation"
                scene.audio.bg_curve = "steady"
            else:
                scene.scene_type = "reveal"
                scene.audio.bg_curve = "climax"
                scene.audio.silence_before_reveal = True

        return scenes
