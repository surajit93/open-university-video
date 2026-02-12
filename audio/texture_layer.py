# audio/texture_layer.py

class TextureLayer:

    def apply_textures(self, scene: dict) -> dict:
        """
        Adds ambient layer + hits based on scene type.
        """

        scene_type = scene.get("scene_type", "analysis")

        texture_profile = {
            "ambient_pad": False,
            "twist_hit": False,
            "transition_swoosh": False
        }

        if scene_type == "tension":
            texture_profile["ambient_pad"] = True

        if scene_type == "twist":
            texture_profile["ambient_pad"] = True
            texture_profile["twist_hit"] = True

        if scene_type == "transition":
            texture_profile["transition_swoosh"] = True

        scene["audio_texture"] = texture_profile

        return scene
