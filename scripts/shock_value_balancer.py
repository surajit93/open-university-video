# scripts/shock_value_balancer.py

import re
from typing import Dict


class ShockValueBalancer:
    def __init__(self, min_ratio: float = 0.8, max_ratio: float = 2.5):
        """
        ratio = shock_density / fact_density
        """
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio

        self.shock_words = [
            "collapse", "destroy", "panic", "chaos", "crisis",
            "catastrophe", "explosion", "fear", "disaster", "shocking"
        ]

    def _shock_density(self, text: str) -> int:
        count = 0
        lower = text.lower()
        for word in self.shock_words:
            count += lower.count(word)
        return count

    def _fact_density(self, text: str) -> int:
        numbers = len(re.findall(r"\d+", text))
        named_entities = len(re.findall(r"\b[A-Z][a-z]{2,}\b", text))
        return numbers + named_entities

    def analyze(self, script: str) -> Dict:
        shock = self._shock_density(script)
        fact = self._fact_density(script)

        if fact == 0:
            ratio = float("inf")
        else:
            ratio = shock / fact

        status = "balanced"
        if ratio < self.min_ratio:
            status = "too_logical"
        elif ratio > self.max_ratio:
            status = "too_shock_heavy"

        return {
            "shock_density": shock,
            "fact_density": fact,
            "ratio": ratio,
            "status": status
        }

    def enforce(self, script: str):
        result = self.analyze(script)

        if result["status"] != "balanced":
            raise ValueError(
                f"Shock/Value imbalance detected: {result['status']} "
                f"(ratio={result['ratio']:.2f})"
            )

        return result
