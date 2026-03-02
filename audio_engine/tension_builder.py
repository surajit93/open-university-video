"""
tension_builder.py
Applies intensity envelope to background music.
"""

import numpy as np
import soundfile as sf


class TensionBuilder:

    def apply_curve(self, audio_path: str, curve: np.ndarray, output_path: str):

        data, sr = sf.read(audio_path)

        if len(data.shape) == 2:
            mono = data.mean(axis=1)
        else:
            mono = data

        scaled = np.zeros_like(mono)

        min_len = min(len(curve), len(mono))

        for i in range(min_len):
            scaled[i] = mono[i] * curve[i]

        sf.write(output_path, scaled, sr)
        return output_path
