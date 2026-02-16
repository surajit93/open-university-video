#scripts/viral_dna_engine.py

import re
from statistics import mean


class ViralDNAEngine:
    """
    Extracts emotional pattern density from top scripts.
    """

    EMOTION_TERMS = [
        "shocking", "collapse", "destroy",
        "exposed", "hidden", "secret",
        "risk", "threat", "danger"
    ]

    def extract_density(self, script: str) -> float:
        lower = script.lower()
        count = sum(1 for word in self.EMOTION_TERMS if word in lower)
        length_factor = max(len(script.split()), 1)
        return round(count / length_factor * 100, 3)

    def reweight_topic_score(self, base_score: float, script: str):
        density = self.extract_density(script)
        bonus = min(density / 10, 0.3)
        return round(base_score + bonus, 3)
