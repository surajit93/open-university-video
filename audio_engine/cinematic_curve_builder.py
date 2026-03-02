"""
cinematic_curve_builder.py
Builds full-video intensity envelope (0.0 → 1.0 scale).
"""

from typing import List
import numpy as np


class CinematicCurveBuilder:

    def build_curve(self, total_duration: float) -> np.ndarray:
        """
        Creates 3-act cinematic envelope.
        """

        fps = 100  # resolution
        total_frames = int(total_duration * fps)

        curve = np.zeros(total_frames)

        for i in range(total_frames):
            progress = i / total_frames

            # Act 1: rising
            if progress < 0.2:
                curve[i] = 0.3 + 0.4 * progress

            # Act 2: tension sustain
            elif progress < 0.8:
                curve[i] = 0.6 + 0.1 * np.sin(progress * 10)

            # Act 3: climax
            else:
                curve[i] = 0.7 + 0.3 * (progress - 0.8) * 5

        return np.clip(curve, 0, 1)
