# scripts/ad_friendly_scorer.py

class AdFriendlyScorer:

    RISK_WORDS = [
        "collapse",
        "war",
        "destroy",
        "crisis",
        "death",
        "apocalypse",
    ]

    def score(self, script: str) -> float:
        script_lower = script.lower()

        risk_hits = sum(1 for word in self.RISK_WORDS if word in script_lower)

        if risk_hits == 0:
            return 1.0
        elif risk_hits <= 2:
            return 0.9
        elif risk_hits <= 4:
            return 0.75
        else:
            return 0.6
