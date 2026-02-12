# audio/dynamic_emphasis.py

class DynamicEmphasis:

    def apply_emphasis(self, scene: dict) -> dict:
        """
        Enhances key moments in narration.
        """

        if "twist_line" in scene:
            scene["audio_emphasis"] = {
                "pre_pause_ms": 250,
                "volume_boost_db": 2.5
            }
        else:
            scene["audio_emphasis"] = {
                "pre_pause_ms": 0,
                "volume_boost_db": 0
            }

        return scene
