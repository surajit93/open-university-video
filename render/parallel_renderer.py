# render/parallel_renderer.py

from multiprocessing import Pool, cpu_count
from typing import List, Dict
from render.scene_composer import SceneComposer


def _compose_single(scene_data: Dict):
    composer = SceneComposer()
    return composer.compose_scene(scene_data)


class ParallelRenderer:

    def __init__(self, workers: int = None):
        self.workers = workers or max(1, cpu_count() - 1)

    def render_scenes(self, scenes: List[Dict]) -> List[Dict]:
        with Pool(self.workers) as pool:
            results = pool.map(_compose_single, scenes)
        return results
