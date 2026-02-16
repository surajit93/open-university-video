# render/parallel_scene_executor.py

from multiprocessing import Pool, cpu_count
from typing import List, Dict, Callable


def _build_single(args):
    build_fn, scene_data = args
    return build_fn(scene_data)


def build_scenes_parallel(
    scenes: List[Dict],
    build_function: Callable,
    max_workers: int = None
) -> List[Dict]:
    """
    Parallel scene builder.
    Does NOT modify existing composer.
    Pure additive scaling layer.
    """

    if not scenes:
        return []

    workers = max_workers or max(1, cpu_count() - 1)

    with Pool(processes=workers) as pool:
        results = pool.map(
            _build_single,
            [(build_function, scene) for scene in scenes]
        )

    return results
