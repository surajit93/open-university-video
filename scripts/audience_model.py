# scripts/audience_model.py

from typing import Dict


class AudienceModel:

    archetypes = {
        "fear_driven": ["risk", "collapse", "danger", "crisis"],
        "tech_enthusiast": ["ai", "automation", "innovation", "future"],
        "career_anxious": ["jobs", "replace", "career", "skills"],
        "curious_generalist": ["why", "how", "what if", "explained"]
    }

    def score_script(self, script_text: str) -> Dict:
        script_lower = script_text.lower()
        scores = {}

        for archetype, keywords in self.archetypes.items():
            score = sum(script_lower.count(k) for k in keywords)
            scores[archetype] = score

        total = sum(scores.values()) or 1

        normalized = {
            k: round(v / total, 3)
            for k, v in scores.items()
        }

        return normalized
