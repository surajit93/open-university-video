"""
visual_decision_engine.py
Hybrid routing logic for AI vs Stock.
"""

import logging
from scene_engine.scene_schema import Scene
from image_engine.prompt_enhancer import PromptEnhancer
from image_engine.ai_generator import AIGenerator
from image_engine.stock_fetcher import StockFetcher
from image_engine.image_cache_manager import ImageCacheManager


logger = logging.getLogger("VisualDecisionEngine")


class VisualDecisionEngine:

    ABSTRACT_KEYWORDS = [
        "bias", "illusion", "pattern", "cognitive", "psychological",
        "hidden", "mechanism", "loop"
    ]

    def __init__(self):
        self.prompt_enhancer = PromptEnhancer()
        self.ai_generator = AIGenerator()
        self.stock_fetcher = StockFetcher()
        self.cache = ImageCacheManager()

    def resolve(self, scene: Scene):

        concept = scene.visual.concept
        mode = self._decide_mode(concept)

        cache_key = f"{mode}:{concept}:{scene.visual.style_profile}"
        cached = self.cache.get_cached_path(cache_key, mode)

        if cached:
            logger.info(f"Using cached image: {cached}")
            return cached

        if mode == "ai":
            prompt = self.prompt_enhancer.enhance(
                concept,
                scene.visual.style_profile
            )
            image_bytes = self.ai_generator.generate(prompt)
        else:
            image_bytes = self.stock_fetcher.fetch(concept)

        return self.cache.store(cache_key, mode, image_bytes)

    def _decide_mode(self, concept: str) -> str:

        concept_lower = concept.lower()

        if any(keyword in concept_lower for keyword in self.ABSTRACT_KEYWORDS):
            return "ai"

        return "stock"
