"""
rhythm_sync.py
Beat-based animation timing system.
"""

import numpy as np


class RhythmSync:

    def calculate_word_timings(self, text: str, duration: float):
        words = text.split()
        word_count = len(words)

        base_interval = duration / max(word_count, 1)

        timings = []
        current = 0.0

        for word in words:
            timings.append((word, current))
            current += base_interval

        return timings

    def ease_out(self, t):
        return 1 - (1 - t) ** 3

    def pulse_scale(self, t, base=1.0, intensity=0.3):
        return base + intensity * np.sin(2 * np.pi * t)
