"""
kinetic_text.py
Word-by-word animated typography engine.
"""

from moviepy.editor import TextClip, CompositeVideoClip
from typography.rhythm_sync import RhythmSync
from typography.shock_word_highlighter import ShockWordHighlighter
from typography.text_style_registry import TextStyleRegistry


class KineticText:

    def __init__(self):
        self.rhythm = RhythmSync()
        self.highlighter = ShockWordHighlighter()
        self.styles = TextStyleRegistry()

    def build(self, text, duration, highlight_words=None):

        style = self.styles.get("kinetic_bold")
        highlight_words = highlight_words or []

        timings = self.rhythm.calculate_word_timings(text, duration)

        clips = []

        for word, start_time in timings:

            word_duration = duration - start_time

            if word in highlight_words:
                clip = self.highlighter.build_clip(word, style, word_duration)
            else:
                clip = TextClip(
                    word,
                    font=style.font,
                    fontsize=style.font_size,
                    color=style.color,
                    stroke_color=style.stroke_color,
                    stroke_width=style.stroke_width
                ).set_duration(word_duration)

            clip = clip.set_start(start_time)
            clip = clip.set_position(("center", "center"))

            clips.append(clip)

        return CompositeVideoClip(clips)
