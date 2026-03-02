"""
kenburns.py
Slow cinematic zoom & pan.
"""

from moviepy.editor import ImageClip
import numpy as np


class KenBurnsMotion:

    def apply(self, image_path: str, duration: float):

        clip = ImageClip(image_path).set_duration(duration)

        def zoom(t):
            scale = 1 + 0.05 * (t / duration)
            return scale

        return clip.resize(lambda t: zoom(t))
