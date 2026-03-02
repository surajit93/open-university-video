"""
beat_sync.py
Detects beats for SFX sync.
"""

import librosa


class BeatSync:

    def detect_beats(self, audio_path: str):
        y, sr = librosa.load(audio_path)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        beat_times = librosa.frames_to_time(beats, sr=sr)

        return beat_times.tolist()
