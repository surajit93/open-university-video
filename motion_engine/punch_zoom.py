"""
punch_zoom.py
Fast impact zoom for hooks & climax.
"""

from moviepy.editor import ImageClip


class PunchZoomMotion:

    def apply(self, image_path: str, duration: float):

        clip = ImageClip(image_path).set_duration(duration)

        def scale(t):
            if t < 0.3:
                return 1 + (0.3 - t) * 0.8
            return 1.0

        return clip.resize(lambda t: scale(t))
