# scripts/style_evolution_manager.py

class StyleEvolutionManager:

    def should_refresh(self, total_uploads: int) -> bool:
        return total_uploads % 30 == 0

    def evolve_style(self, config: dict) -> dict:
        """
        Micro-shifts, not brand reset.
        """

        accent = config.get("accent_color", "#FF4C4C")

        # Slight shift example (mock logic)
        if accent == "#FF4C4C":
            config["accent_color"] = "#FF6A3D"
        else:
            config["accent_color"] = "#FF4C4C"

        config["animation_curve"] = "ease-in-out-refined"

        return config
