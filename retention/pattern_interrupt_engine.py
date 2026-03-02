"""
pattern_interrupt_engine.py
Injects rapid perceptual reset bursts.
Used at psychologically calculated fatigue windows.
"""

from moviepy.editor import CompositeVideoClip, vfx
import numpy as np


class PatternInterruptEngine:

    def __init__(self, interrupt_interval: float = 75.0, duration: float = 0.4):
        self.interval = interrupt_interval
        self.duration = duration

    def apply(self, clip):

        duration = clip.duration
        interrupt_times = np.arange(self.interval, duration, self.interval)

        base = clip
        overlays = []

        for t in interrupt_times:

            segment = base.subclip(t, min(t + self.duration, duration))

            # High contrast + slight color inversion blend
            segment = segment.fx(vfx.lum_contrast, 25, 60, 128)
            segment = segment.fx(vfx.colorx, 1.2)

            segment = segment.set_start(t)

            overlays.append(segment)

        return CompositeVideoClip([base] + overlays)
