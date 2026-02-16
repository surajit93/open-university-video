#scripts/psychological_hook_engine.py

import re


class PsychologicalHookEngine:
    """
    Identity-threat + existential framing scorer.
    Topic MUST pass threshold or gets rejected.
    """

    THREAT_KEYWORDS = [
        "replace", "collapse", "die", "destroy", "eliminate",
        "control", "lose", "risk", "threat", "danger",
        "end", "crisis", "exposed", "ban", "outlaw"
    ]

    IDENTITY_TERMS = [
        "you", "your", "your job", "your future",
        "your family", "your country", "your brain"
    ]

    EXISTENTIAL_TERMS = [
        "forever", "irreversible", "permanent",
        "no going back", "inevitable", "unstoppable"
    ]

    def __init__(self, threshold=0.6):
        self.threshold = threshold

    def _score_keywords(self, text, keywords):
        text = text.lower()
        count = sum(1 for k in keywords if k in text)
        return min(count / 5, 1.0)

    def score_topic(self, title: str) -> float:
        threat_score = self._score_keywords(title, self.THREAT_KEYWORDS)
        identity_score = self._score_keywords(title, self.IDENTITY_TERMS)
        existential_score = self._score_keywords(title, self.EXISTENTIAL_TERMS)

        # Weighted psychological dominance
        final_score = (
            threat_score * 0.4 +
            identity_score * 0.3 +
            existential_score * 0.3
        )

        return round(final_score, 3)

    def enforce(self, title: str):
        score = self.score_topic(title)
        if score < self.threshold:
            raise Exception(
                f"Psychological hook failed. Score={score} below threshold {self.threshold}"
            )
        return score
