"""
chapter_structurer.py
Breaks long-form video into logical chapters.
"""

from typing import List
from scene_engine.scene_schema import Scene


class ChapterStructurer:

    CHAPTER_SIZE = 20

    def assign_chapters(self, scenes: List[Scene]) -> List[Scene]:
        for idx, scene in enumerate(scenes):
            chapter_index = idx // self.CHAPTER_SIZE
            scene.chapter = f"Chapter {chapter_index + 1}"

        return scenes
