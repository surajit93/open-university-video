"""
silence_dropper.py
Injects dramatic silence before reveal scenes.
"""

import numpy as np
import soundfile as sf


class SilenceDropper:

    def apply(self, audio_path: str, drop_time: float, duration: float, output_path: str):

        data, sr = sf.read(audio_path)

        start_sample = int(drop_time * sr)
        end_sample = int((drop_time + duration) * sr)

        data[start_sample:end_sample] = 0

        sf.write(output_path, data, sr)
        return output_path
