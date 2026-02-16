# scripts/topic_ranker.py

import logging
from typing import Dict, List

from scripts.quality_threshold_gate import QualityThresholdGate


class TopicRanker:

    def __init__(self):
        self.gate = QualityThresholdGate()

    # ==========================================================
    # EXISTING SCORING LOGIC (UNCHANGED)
    # ==========================================================

    def score_topic(self, topic: Dict) -> Dict:
        """
        topic example:
        {
            "title": "...",
            "search_demand": 0.7,
            "emotional_intensity": 0.8,
            "controversy": 0.5,
            "evergreen": 0.6,
            "cluster_fit": 0.9,
            "depth_score": 0.6,
            "curiosity_score": 0.7
        }
        """

        weights = {
            "search_demand": 0.25,
            "emotional_intensity": 0.20,
            "controversy": 0.15,
            "evergreen": 0.20,
            "cluster_fit": 0.20
        }

        score = 0
        for key, weight in weights.items():
            score += topic.get(key, 0) * weight

        return {
            "title": topic["title"],
            "priority_score": round(score, 3),
            "depth_score": topic.get("depth_score", 0.5),
            "curiosity_score": topic.get("curiosity_score", 0.5)
        }

    def rank(self, topics: List[Dict]) -> List[Dict]:
        scored = [self.score_topic(t) for t in topics]
        return sorted(scored, key=lambda x: x["priority_score"], reverse=True)

    # ==========================================================
    # NEW: STRICT QUALITY GATE ENFORCEMENT
    # ==========================================================

    def select_top_valid(self, topics: List[Dict]) -> Dict:
        """
        Returns first topic that passes strict quality threshold.
        Raises exception if none pass.
        """

        ranked_topics = self.rank(topics)

        for topic in ranked_topics:

            gate_result = self.gate.evaluate(
                topic_score=topic["priority_score"],
                depth_score=topic["depth_score"],
                curiosity_score=topic["curiosity_score"]
            )

            if not gate_result["approved"]:
                logging.warning(
                    f"[QUALITY REJECTED] {topic['title']} | "
                    f"Reasons: {gate_result['reasons']}"
                )
                continue

            logging.info(
                f"[QUALITY APPROVED] {topic['title']} | "
                f"Score={topic['priority_score']}"
            )

            return topic

        logging.error("All candidate topics rejected by quality gate.")
        raise Exception("No topics passed quality threshold.")
