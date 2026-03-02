"""
countdown_visualizer.py
High tension countdown animation.
"""

from moviepy.editor import TextClip, CompositeVideoClip


class CountdownVisualizer:

    def build(self, seconds: int):

        clips = []

        for i in range(seconds, 0, -1):
            clip = TextClip(
                str(i),
                font="Montserrat-Black",
                fontsize=180,
                color="#FF0055",
                stroke_color="black",
                stroke_width=6
            ).set_duration(1)

            def pulse(t):
                return 1 + 0.3 * t

            clip = clip.resize(lambda t: pulse(t))
            clip = clip.set_position("center")
            clip = clip.set_start(seconds - i)

            clips.append(clip)

        return CompositeVideoClip(clips)
