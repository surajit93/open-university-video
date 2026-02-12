# audio/voice_selector.py

import random


class VoiceSelector:

    def __init__(self, config: dict):
        self.available_voices = config.get(
            "tts_voices",
            ["voice_a", "voice_b", "voice_c"]
        )

    def select_voice(self, scene_type: str, emotional_intensity: float) -> dict:
        """
        scene_type: hook | tension | analysis | twist | resolution
        emotional_intensity: 0.0 – 1.0
        """

        base_voice = random.choice(self.available_voices)

        prosody = self._prosody_profile(scene_type, emotional_intensity)

        return {
            "voice": base_voice,
            "rate": prosody["rate"],
            "pitch": prosody["pitch"],
            "volume_gain_db": prosody["volume"]
        }

    def _prosody_profile(self, scene_type: str, intensity: float):
        if scene_type == "hook":
            return {
                "rate": 1.05,
                "pitch": "+2%",
                "volume": 1.5
            }

        if scene_type == "twist":
            return {
                "rate": 0.92,
                "pitch": "-1%",
                "volume": 2.0
            }

        if scene_type == "analysis":
            return {
                "rate": 0.98,
                "pitch": "0%",
                "volume": 0
            }

        # default scaling
        return {
            "rate": 1.0 + (intensity * 0.05),
            "pitch": f"{intensity * 2}%",
            "volume": intensity * 2
        }
