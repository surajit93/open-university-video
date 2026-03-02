"""
mid_video_reset.py
Engineered mid-point cognitive refresh for long-form retention.
Applies structured reset near 55% timeline.
"""

from moviepy.editor import CompositeVideoClip, vfx


class MidVideoReset:

    def __init__(self, reset_window: float = 3.0):
        self.reset_window = reset_window

    def apply(self, clip):

        duration = clip.duration
        midpoint = duration * 0.55

        reset_end = min(midpoint + self.reset_window, duration)

        before = clip.subclip(0, midpoint)

        reset_segment = clip.subclip(midpoint, reset_end)

        # Visual refresh
        reset_segment = reset_segment.fx(vfx.colorx, 1.3)
        reset_segment = reset_segment.fx(vfx.lum_contrast, 20, 45, 128)

        after = clip.subclip(reset_end, duration)

        before = before.set_start(0)
        reset_segment = reset_segment.set_start(midpoint)
        after = after.set_start(reset_end)

        return CompositeVideoClip([before, reset_segment, after])
