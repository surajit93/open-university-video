"""
chapter_intro_text.py
Large cinematic chapter break typography.
"""

from moviepy.editor import TextClip


class ChapterIntroText:

    def build(self, chapter_title: str, duration: float):

        clip = TextClip(
            chapter_title.upper(),
            font="Montserrat-ExtraBold",
            fontsize=140,
            color="#00FFC6",
            stroke_color="black",
            stroke_width=4
        ).set_duration(duration)

        def fade_scale(t):
            if t < 1:
                return 1.2 - 0.2 * t
            return 1.0

        return clip.resize(lambda t: fade_scale(t)).set_position("center")
