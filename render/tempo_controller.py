# render/tempo_controller.py

from typing import List, Dict
import time
import logging


class TempoController:

    def validate_tempo(self, scenes: List[Dict]) -> List[Dict]:
        validated = []

        for scene in scenes:
            duration = scene.get("duration", 8)

            if duration > 7:
                scene["duration"] = 7

            validated.append(scene)

        return validated

    def enforce_overlay_injection(self, scene: Dict) -> Dict:
        if not scene.get("overlay_injected"):
            scene["overlay_injected"] = True
            scene["overlay_type"] = "micro_transition_graphic"

        return scene

    # --------------------------------
    # 🔥 NEW: RENDER BENCHMARK LOGGING
    # --------------------------------

    def benchmark_render(self, render_callable, *args, **kwargs):
        start = time.time()
        result = render_callable(*args, **kwargs)
        duration = time.time() - start
        logging.info(f"[RENDER BENCHMARK] {duration:.3f}s")
        return result
