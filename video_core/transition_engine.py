"""
transition_engine.py
High-retention fast-cut transition system.
"""

from moviepy.editor import concatenate_videoclips, CompositeVideoClip


class TransitionEngine:

    def __init__(self, transition_duration=0.3):
        self.transition_duration = transition_duration

    def apply_transitions(self, clips):

        processed = []

        for i in range(len(clips) - 1):

            current = clips[i]
            next_clip = clips[i + 1]

            current = current.crossfadeout(self.transition_duration)
            next_clip = next_clip.crossfadein(self.transition_duration)

            processed.append(current)

        processed.append(clips[-1])

        return concatenate_videoclips(processed, method="compose")
