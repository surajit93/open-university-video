"""
scene_validator.py
Ensures scenes comply with cinematic contract.
"""

from typing import List
from scene_engine.scene_schema import Scene


class SceneValidator:

    MIN_DURATION = 3.5
    MAX_DURATION = 7.0

    def validate(self, scenes: List[Scene]) -> List[Scene]:
        validated = []
        for scene in scenes:
            if scene.duration < self.MIN_DURATION:
                scene.duration = self.MIN_DURATION
            if scene.duration > self.MAX_DURATION:
                scene.duration = self.MAX_DURATION

            if not scene.visual.camera_motion:
                scene.visual.camera_motion = "kenburns"

            validated.append(scene)

        return validated
