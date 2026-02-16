from typing import List, Dict
from scripts.thumbnail_renderer import render_thumbnail
import os
import hashlib

# 🔥 NEW
try:
    from scripts.thumbnail_swap_scheduler import schedule_thumbnail_swap
except Exception:
    def schedule_thumbnail_swap(*args, **kwargs):
        pass


class ThumbnailVariationGenerator:

    def __init__(self):
        os.makedirs("outputs/thumbnails", exist_ok=True)

    def score_contrast(self, text: str) -> float:
        return min(len(text) / 50, 1.0)

    def score_emotion(self, text: str) -> float:
        emotional_words = ["shock", "collapse", "war", "future", "destroy", "secret"]
        score = 0
        for word in emotional_words:
            if word in text.lower():
                score += 0.15
        return min(score, 1.0)

    def score_variant(self, variant: Dict) -> float:
        word_penalty = abs(4 - variant["word_count"]) * 0.05
        score = (
            variant["contrast_score"] * 0.4 +
            variant["emotion_score"] * 0.5 -
            word_penalty
        )
        return round(score, 3)

    # 🔥 NEW: Packaging entropy tracking
    def _entropy_signature(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def generate_and_rank(self, title_variants: List[str]) -> List[Dict]:
        scored_variants = []

        for i, title in enumerate(title_variants):
            contrast_score = self.score_contrast(title)
            emotion_score = self.score_emotion(title)

            variant = {
                "text": title,
                "contrast_score": contrast_score,
                "emotion_score": emotion_score,
                "word_count": len(title.split())
            }

            variant["score"] = self.score_variant(variant)

            output_path = f"outputs/thumbnails/thumb_{i}.png"

            render_thumbnail(
                text=title,
                bg_color="#111111",
                output_path=output_path
            )

            variant["image_path"] = output_path

            # 🔥 NEW: Entropy signature
            variant["entropy_signature"] = self._entropy_signature(title)

            scored_variants.append(variant)

        if not scored_variants:
            raise RuntimeError("No thumbnail variants generated.")

        scored_variants.sort(key=lambda x: x["score"], reverse=True)

        # 🔥 NEW: A/B registration hook (first two variants)
        if len(scored_variants) >= 2:
            top = scored_variants[0]
            second = scored_variants[1]
            schedule_thumbnail_swap(
                video_id="pending_video",
                original=top["image_path"],
                alternate=second["image_path"]
            )

        return scored_variants
