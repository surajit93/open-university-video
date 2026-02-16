#script/visual_psychology_engine.py

import random
from typing import Dict, List


class VisualPsychologyEngine:
    """
    BrightSide-level visual psychology control.

    - Contrast cycling
    - Pattern disruption injection
    - Movement spike timing
    """

    def __init__(self):
        self.contrast_cycle = ["low", "medium", "high"]
        self.last_contrast_index = 0

    # ==========================================================
    # CONTRAST CYCLE ENGINE
    # ==========================================================

    def apply_contrast_cycle(self, scene: Dict) -> Dict:
        """
        Enforces visual contrast alternation across scenes.
        """

        level = self.contrast_cycle[self.last_contrast_index]

        scene["contrast_level"] = level

        self.last_contrast_index = (
            (self.last_contrast_index + 1)
            % len(self.contrast_cycle)
        )

        return scene

    # ==========================================================
    # PATTERN DISRUPTION
    # ==========================================================

    def inject_pattern_disruption(self, scene: Dict, index: int) -> Dict:
        """
        Every few scenes → inject pattern interrupt.
        """

        if index % 4 == 0:
            scene["pattern_disruption"] = True
            scene["disruption_type"] = random.choice([
                "micro_zoom_jump",
                "flash_overlay",
                "quick_cut",
                "scale_pop"
            ])
        else:
            scene["pattern_disruption"] = False

        return scene

    # ==========================================================
    # MOVEMENT SPIKE TIMING
    # ==========================================================

    def inject_movement_spike(self, scene: Dict, index: int) -> Dict:
        """
        Inject movement intensity spike every 3rd scene.
        """

        if index % 3 == 0:
            scene["movement_spike"] = True
            scene["motion_intensity"] = "high"
        else:
            scene["movement_spike"] = False
            scene["motion_intensity"] = "normal"

        return scene

    # ==========================================================
    # MASTER PIPELINE
    # ==========================================================

    def process_scene(self, scene: Dict, index: int) -> Dict:
        scene = self.apply_contrast_cycle(scene)
        scene = self.inject_pattern_disruption(scene, index)
        scene = self.inject_movement_spike(scene, index)
        return scene
