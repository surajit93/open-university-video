"""
scene_composer.py
Transforms a Scene object into a fully composed cinematic clip.
"""

from moviepy.editor import (
    CompositeVideoClip,
    AudioFileClip,
)
from image_engine.visual_decision_engine import VisualDecisionEngine
from motion_engine.motion_template_registry import MotionTemplateRegistry
from typography.kinetic_text import KineticText
from typography.chapter_intro_text import ChapterIntroText
from typography.countdown_visualizer import CountdownVisualizer


class SceneComposer:

    def __init__(self):
        self.visual_engine = VisualDecisionEngine()
        self.motion_registry = MotionTemplateRegistry()
        self.kinetic_text = KineticText()
        self.chapter_text = ChapterIntroText()
        self.countdown_visualizer = CountdownVisualizer()

    def compose(self, scene, narration_audio_path=None):

        # 1️⃣ Resolve image
        image_path = self.visual_engine.resolve(scene)

        # 2️⃣ Apply motion
        motion_template = self.motion_registry.get(scene.visual.camera_motion)
        base_clip = motion_template.apply(str(image_path), scene.duration)

        # 3️⃣ Typography
        text_clip = self.kinetic_text.build(
            text=scene.narration,
            duration=scene.duration,
            highlight_words=scene.typography.highlight_words
        )

        layers = [base_clip, text_clip]

        # 4️⃣ Chapter intro override
        if scene.scene_type == "hook" and scene.chapter:
            chapter_clip = self.chapter_text.build(scene.chapter, 3)
            chapter_clip = chapter_clip.set_start(0)
            layers.append(chapter_clip)

        # 5️⃣ Countdown logic
        if "countdown" in scene.narration.lower():
            countdown_clip = self.countdown_visualizer.build(5)
            layers.append(countdown_clip)

        final_clip = CompositeVideoClip(layers)

        # 6️⃣ Attach narration audio if provided
        if narration_audio_path:
            audio_clip = AudioFileClip(narration_audio_path)
            final_clip = final_clip.set_audio(audio_clip)

        return final_clip.set_duration(scene.duration)
