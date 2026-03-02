"""
glitch_hit.py
Micro glitch burst for pattern interrupt.
"""

from moviepy.editor import ImageClip
import numpy as np


class GlitchHitMotion:

    def apply(self, image_path: str, duration: float):

        clip = ImageClip(image_path).set_duration(duration)

        def glitch(get_frame, t):
            frame = get_frame(t)
            if int(t * 10) % 7 == 0:
                frame[:, :, 0] = np.roll(frame[:, :, 0], 5, axis=1)
            return frame

        return clip.fl(glitch)
