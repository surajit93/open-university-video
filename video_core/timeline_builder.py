"""
timeline_builder.py
Builds full 8–12 minute timeline safely in memory.
"""

from video_core.scene_composer import SceneComposer
from video_core.transition_engine import TransitionEngine
from video_core.retention_controller import RetentionController


class TimelineBuilder:

    def __init__(self):
        self.composer = SceneComposer()
        self.transition_engine = TransitionEngine()
        self.retention_controller = RetentionController()

    def build(self, scenes):

        clips = []

        for scene in scenes:
            clip = self.composer.compose(scene)
            clip = self.retention_controller.enhance(clip, scene)
            clips.append(clip)

        final_video = self.transition_engine.apply_transitions(clips)

        return final_video
