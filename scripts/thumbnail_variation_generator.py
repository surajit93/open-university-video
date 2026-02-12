# scripts/thumbnail_variation_generator.py

from typing import List, Dict


class ThumbnailVariationGenerator:

    def score_variant(self, variant: Dict) -> float:
        """
        variant:
        {
            "text": "...",
            "contrast_score": 0.8,
            "emotion_score": 0.7,
            "word_count": 4
        }
        """

        word_penalty = abs(4 - variant["word_count"]) * 0.05
        score = (
            variant["contrast_score"] * 0.4 +
            variant["emotion_score"] * 0.5 -
            word_penalty
        )

        return round(score, 3)

    def rank_variants(self, variants: List[Dict]) -> List[Dict]:
        for v in variants:
            v["score"] = self.score_variant(v)

        return sorted(variants, key=lambda x: x["score"], reverse=True)[:2]
