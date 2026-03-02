"""
parallax.py
Simulated depth drift effect.
"""

from moviepy.editor import ImageClip
import numpy as np


class ParallaxMotion:

    def apply(self, image_path: str, duration: float):

        clip = ImageClip(image_path).set_duration(duration)

        w, h = clip.size

        def drift(get_frame, t):
            frame = get_frame(t)
            shift = int(20 * (t / duration))
            return np.roll(frame, shift, axis=1)

        return clip.fl(drift)
