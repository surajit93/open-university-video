# scripts/semantic_repetition_guard.py

import re
from collections import Counter
from typing import Dict


class SemanticRepetitionGuard:

    def _extract_phrases(self, text: str):
        sentences = re.split(r'[.!?]', text)
        phrases = []

        for s in sentences:
            words = s.strip().split()
            if len(words) > 4:
                phrases.append(" ".join(words[:5]).lower())

        return phrases

    def analyze(self, script: str) -> Dict:
        phrases = self._extract_phrases(script)
        counts = Counter(phrases)

        repeated = {k: v for k, v in counts.items() if v > 1}

        repetition_score = sum(repeated.values())

        return {
            "repetition_score": repetition_score,
            "repeated_phrases": repeated
        }

    def enforce(self, script: str, threshold: int = 3):
        result = self.analyze(script)

        if result["repetition_score"] >= threshold:
            raise ValueError(
                f"Semantic repetition detected: score={result['repetition_score']}"
            )

        return result
