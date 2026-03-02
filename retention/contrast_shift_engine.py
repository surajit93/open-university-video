"""
contrast_shift_engine.py
Arc-aware contrast cycling to prevent long-form fatigue.
"""

from moviepy.editor import CompositeVideoClip, vfx
import numpy as np


class ContrastShiftEngine:

    def __init__(self, cycle_duration: float = 90.0):
        self.cycle_duration = cycle_duration

    def apply(self, clip):

        duration = clip.duration
        segments = []

        current = 0.0
        toggle = False

        while current < duration:

            end = min(current + self.cycle_duration, duration)
            segment = clip.subclip(current, end)

            if toggle:
                segment = segment.fx(vfx.colorx, 1.08)
            else:
                segment = segment.fx(vfx.lum_contrast, 8, 20, 128)

            segment = segment.set_start(current)

            segments.append(segment)

            toggle = not toggle
            current += self.cycle_duration

        return CompositeVideoClip(segments)
