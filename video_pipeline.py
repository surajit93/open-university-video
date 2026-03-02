"""
video_pipeline.py
Master orchestration engine for 8–12 min cinematic retention videos.
Enterprise-grade structured pipeline.
"""

from pathlib import Path
from typing import List
import logging
import json

from scene_engine.scene_generator import SceneGenerator
from scene_engine.scene_validator import SceneValidator
from scene_engine.arc_designer import ArcDesigner
from scene_engine.pacing_controller import PacingController
from scene_engine.chapter_structurer import ChapterStructurer
from scene_engine.scene_schema import Scene

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VideoPipeline")


class VideoPipeline:
    def __init__(self, topic_payload: dict):
        self.topic_payload = topic_payload
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        self.generator = SceneGenerator()
        self.validator = SceneValidator()
        self.arc_designer = ArcDesigner()
        self.pacing_controller = PacingController()
        self.chapter_structurer = ChapterStructurer()

    def run(self) -> List[Scene]:
        logger.info("Starting scene generation...")
        scenes = self.generator.generate(self.topic_payload)

        logger.info("Validating scenes...")
        scenes = self.validator.validate(scenes)

        logger.info("Applying arc design...")
        scenes = self.arc_designer.apply_multi_arc_structure(scenes)

        logger.info("Applying pacing control...")
        scenes = self.pacing_controller.optimize_timing(scenes)

        logger.info("Structuring chapters...")
        scenes = self.chapter_structurer.assign_chapters(scenes)

        self._persist_scene_plan(scenes)
        logger.info("Pipeline complete.")
        return scenes

    def _persist_scene_plan(self, scenes: List[Scene]) -> None:
        serialized = [scene.to_dict() for scene in scenes]
        with open(self.output_dir / "scene_plan.json", "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2)


if __name__ == "__main__":
    with open("topics.json", "r", encoding="utf-8") as f:
        topic_data = json.load(f)

    pipeline = VideoPipeline(topic_data["topics"][0])
    pipeline.run()
