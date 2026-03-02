"""
music_intensity_mapper.py
Maps scene-level intensity to gain values.
"""

class MusicIntensityMapper:

    INTENSITY_GAIN = {
        "intense": 1.2,
        "rising": 1.0,
        "steady": 0.8,
        "climax": 1.5
    }

    def map_gain(self, scene_type: str) -> float:
        return self.INTENSITY_GAIN.get(scene_type, 1.0)
