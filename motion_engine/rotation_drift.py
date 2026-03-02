"""
rotation_drift.py
Subtle psychological instability effect.
"""

from moviepy.editor import ImageClip


class RotationDriftMotion:

    def apply(self, image_path: str, duration: float):

        clip = ImageClip(image_path).set_duration(duration)

        def angle(t):
            return 2 * (t / duration)

        return clip.rotate(lambda t: angle(t))
