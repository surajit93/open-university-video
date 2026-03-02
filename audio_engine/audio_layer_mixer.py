"""
audio_layer_mixer.py
Professional multi-layer mixer with ducking.
"""

from pydub import AudioSegment


class AudioLayerMixer:

    def mix(self, narration_path: str, music_path: str, output_path: str):

        narration = AudioSegment.from_file(narration_path)
        music = AudioSegment.from_file(music_path)

        # Duck music under narration
        music = music - 10

        combined = music.overlay(narration)

        combined.export(output_path, format="wav")
        return output_path
