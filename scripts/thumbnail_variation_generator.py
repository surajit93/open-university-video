# scripts/thumbnail_variation_generator.py

from typing import List, Dict
# ADD IMPORT
from scripts.thumbnail_renderer import render_thumbnail


def generate_thumbnail_variants(title_variants):
    scored_variants = []

    for i, title in enumerate(title_variants):

        # --- your existing scoring logic ---
        contrast_score = score_contrast(title)
        emotion_score = score_emotion(title)
        composite = (contrast_score * 0.5) + (emotion_score * 0.5)

        output_path = f"outputs/thumbnails/thumb_{i}.png"

        render_thumbnail(
            text=title,
            bg_color="#111111",
            output_path=output_path
        )

        scored_variants.append({
            "title": title,
            "contrast_score": contrast_score,
            "emotion_score": emotion_score,
            "composite_score": composite,
            "image_path": output_path
        })

    scored_variants.sort(key=lambda x: x["composite_score"], reverse=True)

    return scored_variants



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
