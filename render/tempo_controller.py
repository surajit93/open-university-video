# render/tempo_controller.py

from typing import List, Dict
import time
import logging

# 🔥 Rhythm enforcement (unchanged)
try:
    from render.rhythm_enforcer import RhythmEnforcer
except Exception:
    RhythmEnforcer = None

# 🔥 NEW – Visual psychology integration (additive only)
try:
    from render.visual_psychology_engine import VisualPsychologyEngine
except Exception:
    VisualPsychologyEngine = None


class TempoController:

    def __init__(self):
        # 🔥 Existing rhythm engine
        self._rhythm_engine = RhythmEnforcer() if RhythmEnforcer else None

        # 🔥 NEW – visual psychology engine (additive only)
        self._visual_engine = VisualPsychologyEngine() if VisualPsychologyEngine else None

    def validate_tempo(self, scenes: List[Dict]) -> List[Dict]:
        validated = []

        for index, scene in enumerate(scenes):
            duration = scene.get("duration", 8)

            # EXISTING LOGIC (UNCHANGED)
            if duration > 7:
                scene["duration"] = 7

            # 🔥 Apply visual psychology scene processing (additive only)
            if self._visual_engine:
                scene = self._visual_engine.process_scene(scene, index)

            validated.append(scene)

        # 🔥 Apply rhythm enforcement AFTER original tempo logic
        if self._rhythm_engine:
            validated = self._rhythm_engine.process(validated)

        return validated

    def enforce_overlay_injection(self, scene: Dict) -> Dict:
        if not scene.get("overlay_injected"):
            scene["overlay_injected"] = True
            scene["overlay_type"] = "micro_transition_graphic"

        return scene

    # --------------------------------
    # 🔥 RENDER BENCHMARK LOGGING (UNCHANGED)
    # --------------------------------

    def benchmark_render(self, render_callable, *args, **kwargs):
        start = time.time()
        result = render_callable(*args, **kwargs)
        duration = time.time() - start
        logging.info(f"[RENDER BENCHMARK] {duration:.3f}s")
        return result
