#rhythm_enforcer.py

from typing import List, Dict


class RhythmEnforcer:
    """
    Dopamine interval pacing model.

    - Scene pacing spikes
    - Forced break every X seconds
    """

    def __init__(self, break_interval=40):
        self.break_interval = break_interval

    # ==========================================================
    # SCENE BREAK ENFORCEMENT
    # ==========================================================

    def enforce_breaks(self, scenes: List[Dict]) -> List[Dict]:
        """
        Inject forced rhythm break approximately every X seconds.
        """

        elapsed = 0

        for scene in scenes:
            duration = scene.get("duration", 8)
            elapsed += duration

            if elapsed >= self.break_interval:
                scene["rhythm_break"] = True
                scene["break_type"] = "hard_pattern_interrupt"
                elapsed = 0
            else:
                scene["rhythm_break"] = False

        return scenes

    # ==========================================================
    # PACING SPIKES
    # ==========================================================

    def inject_pacing_spikes(self, scenes: List[Dict]) -> List[Dict]:
        """
        Shorten selected scenes to create spike effect.
        """

        for i, scene in enumerate(scenes):
            if i % 5 == 0:
                scene["duration"] = min(scene.get("duration", 8), 5)
                scene["pacing_spike"] = True
            else:
                scene["pacing_spike"] = False

        return scenes

    # ==========================================================
    # MASTER PIPELINE
    # ==========================================================

    def process(self, scenes: List[Dict]) -> List[Dict]:
        scenes = self.inject_pacing_spikes(scenes)
        scenes = self.enforce_breaks(scenes)
        return scenes
