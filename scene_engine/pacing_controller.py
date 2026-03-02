"""
pacing_controller.py
Controls rhythm and micro-pattern interrupts.
"""

from typing import List
from scene_engine.scene_schema import Scene


class PacingController:

    INTERRUPT_INTERVAL = 6

    def optimize_timing(self, scenes: List[Scene]) -> List[Scene]:
        for idx, scene in enumerate(scenes):
            if idx % self.INTERRUPT_INTERVAL == 0:
                scene.retention.pattern_interrupt = True
                scene.retention.contrast_shift = True
                scene.visual.camera_motion = "punch_zoom"

        return scenes
