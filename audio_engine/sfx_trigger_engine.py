"""
sfx_trigger_engine.py
Injects SFX at strategic timestamps.
"""

from pydub import AudioSegment


class SFXTriggerEngine:

    def overlay_sfx(self, base_audio_path: str, sfx_events: list, output_path: str):

        base = AudioSegment.from_file(base_audio_path)

        for event in sfx_events:
            sfx = AudioSegment.from_file(event["file"])
            position = int(event["time"] * 1000)

            base = base.overlay(sfx, position=position)

        base.export(output_path, format="wav")
        return output_path
