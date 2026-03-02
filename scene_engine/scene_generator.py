"""
scene_generator.py
Production-grade long-form cinematic script generator.
8–12 minute retention-optimized structure.
"""

from typing import List
from dataclasses import replace
import math
import random

from scene_engine.scene_schema import (
    Scene,
    VisualConfig,
    TypographyConfig,
    AudioConfig,
    RetentionConfig,
)


class SceneGenerator:
    """
    Generates 8–12 minute structured cinematic scene plan.
    ~140 scenes target.
    """

    TARGET_MINUTES = 10
    AVG_SCENE_DURATION = 5.0
    TARGET_SCENE_COUNT = int((TARGET_MINUTES * 60) / AVG_SCENE_DURATION)

    def generate(self, topic_payload: dict) -> List[Scene]:

        title = topic_payload.get("title", "Untitled Topic")
        domain = topic_payload.get("domain", "general")
        level = topic_payload.get("level", "strategic")

        structured_script = self._build_long_form_script(title, domain, level)

        scenes: List[Scene] = []

        for index, line in enumerate(structured_script):

            scene_type = self._infer_scene_type(index)

            scene = Scene(
                narration=line,
                duration=self.AVG_SCENE_DURATION,
                scene_type=scene_type,
                visual=self._build_visual(line, scene_type),
                typography=self._build_typography(line, scene_type),
                audio=self._build_audio(scene_type),
                retention=self._build_retention(index),
            )

            scenes.append(scene)

        return scenes

    # ==========================================================
    # SCRIPT GENERATION CORE
    # ==========================================================

    def _build_long_form_script(self, title: str, domain: str, level: str) -> List[str]:

        hook = self._hook_block(title)
        tension = self._problem_block(title)
        deep_analysis = self._analysis_block(title)
        escalation = self._escalation_block(title)
        climax = self._reveal_block(title)
        resolution = self._resolution_block(title)

        full_script = (
            hook
            + tension
            + deep_analysis
            + escalation
            + climax
            + resolution
        )

        # Normalize length to target
        if len(full_script) < self.TARGET_SCENE_COUNT:
            deficit = self.TARGET_SCENE_COUNT - len(full_script)
            full_script.extend(self._analysis_block(title, repeat=deficit))

        return full_script[: self.TARGET_SCENE_COUNT]

    # ==========================================================
    # STRUCTURE BLOCKS
    # ==========================================================

    def _hook_block(self, title: str) -> List[str]:
        return [
            f"What if everything you believe about {title} is incomplete?",
            f"Most people never see the real pattern behind {title}.",
            "In the next few minutes, your perspective will permanently shift.",
            "But only if you stay until the end."
        ]

    def _problem_block(self, title: str) -> List[str]:
        return [
            f"The problem with understanding {title} is subtle.",
            "It hides in plain sight.",
            "Your brain filters it out automatically.",
            "And that is exactly why most people never notice it."
        ]

    def _analysis_block(self, title: str, repeat: int = 25) -> List[str]:
        base_lines = []
        for i in range(repeat):
            base_lines.append(
                f"Layer {i+1}: When examining {title}, a deeper mechanism emerges."
            )
            base_lines.append(
                "Patterns begin to reveal a structure most overlook."
            )
            base_lines.append(
                "This is not random. It follows a predictable behavioral loop."
            )
        return base_lines

    def _escalation_block(self, title: str) -> List[str]:
        return [
            "Now here is where it becomes uncomfortable.",
            f"If this pattern in {title} continues unchecked, the consequences multiply.",
            "The system reinforces itself.",
            "And breaking it becomes exponentially harder."
        ]

    def _reveal_block(self, title: str) -> List[str]:
        return [
            "Here is the hidden pivot point.",
            f"The real driver behind {title} is not what it appears to be.",
            "It is leverage.",
            "It is attention.",
            "It is cognitive bias disguised as logic."
        ]

    def _resolution_block(self, title: str) -> List[str]:
        return [
            "Once you see it, you cannot unsee it.",
            f"And that changes how you approach {title} forever.",
            "Because now you understand the underlying mechanism.",
            "And understanding creates power."
        ]

    # ==========================================================
    # SCENE TYPE INFERENCE
    # ==========================================================

    def _infer_scene_type(self, index: int) -> str:
        progress = index / self.TARGET_SCENE_COUNT

        if progress < 0.1:
            return "hook"
        elif progress < 0.5:
            return "tension"
        elif progress < 0.8:
            return "analysis"
        elif progress < 0.95:
            return "climax"
        else:
            return "resolution"

    # ==========================================================
    # VISUAL CONFIG
    # ==========================================================

    def _build_visual(self, line: str, scene_type: str) -> VisualConfig:

        if scene_type in ["hook", "climax"]:
            motion = "punch_zoom"
            style = "high_contrast_neon"
        elif scene_type == "analysis":
            motion = "kenburns"
            style = "cinematic_clean"
        else:
            motion = "parallax"
            style = "dark_tension"

        return VisualConfig(
            mode="ai",
            concept=line,
            style_profile=style,
            camera_motion=motion,
        )

    # ==========================================================
    # TYPOGRAPHY CONFIG
    # ==========================================================

    def _build_typography(self, line: str, scene_type: str) -> TypographyConfig:

        words = line.split()
        highlight = [w for w in words if len(w) > 7][:2]

        effect = "shock_pop" if scene_type in ["hook", "climax"] else "kinetic_slide"

        return TypographyConfig(
            style="kinetic_bold",
            highlight_words=highlight,
            effect=effect,
        )

    # ==========================================================
    # AUDIO CONFIG
    # ==========================================================

    def _build_audio(self, scene_type: str) -> AudioConfig:

        if scene_type == "hook":
            return AudioConfig(
                bg_curve="intense",
                sfx=["whoosh", "bass_hit"],
                silence_before_reveal=False,
            )

        if scene_type == "climax":
            return AudioConfig(
                bg_curve="climax",
                sfx=["riser", "cinematic_hit"],
                silence_before_reveal=True,
            )

        return AudioConfig(
            bg_curve="rising",
            sfx=["tick"],
            silence_before_reveal=False,
        )

    # ==========================================================
    # RETENTION ENGINE
    # ==========================================================

    def _build_retention(self, index: int) -> RetentionConfig:

        pattern_interrupt = (index % 7 == 0)
        contrast_shift = (index % 11 == 0)

        return RetentionConfig(
            pattern_interrupt=pattern_interrupt,
            contrast_shift=contrast_shift,
        )
