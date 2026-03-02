"""
shock_word_highlighter.py
Applies dynamic scale & color pulse to key words.
"""

from moviepy.editor import TextClip
import numpy as np


class ShockWordHighlighter:

    def build_clip(self, word, style, duration):

        base_clip = TextClip(
            word,
            font=style.font,
            fontsize=style.font_size,
            color=style.color,
            stroke_color=style.stroke_color,
            stroke_width=style.stroke_width
        ).set_duration(duration)

        def scale(t):
            if t < 0.4:
                return 1 + (0.4 - t) * 1.2
            return 1.0

        animated = base_clip.resize(lambda t: scale(t))

        return animated
