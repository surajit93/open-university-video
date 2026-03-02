"""
spike_injector.py
Time-windowed micro dopamine spike system.
Applies short intensity bursts at calculated timestamps.
"""

from moviepy.editor import CompositeVideoClip, vfx
import numpy as np


class SpikeInjector:

    def __init__(self, interval_seconds: float = 28.0, spike_duration: float = 0.35):
        self.interval = interval_seconds
        self.spike_duration = spike_duration

    def apply(self, clip):

        duration = clip.duration
        spike_times = np.arange(self.interval, duration, self.interval)

        base = clip

        overlays = []

        for t in spike_times:

            segment = base.subclip(t, min(t + self.spike_duration, duration))

            # Controlled brightness + contrast spike
            segment = segment.fx(vfx.lum_contrast, 15, 35, 128)

            segment = segment.set_start(t)

            overlays.append(segment)

        return CompositeVideoClip([base] + overlays)
