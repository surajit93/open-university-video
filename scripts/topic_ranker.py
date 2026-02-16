# scripts/topic_ranker.py

import logging
from typing import Dict, List

from scripts.quality_threshold_gate import QualityThresholdGate
from scripts.revenue_tracker import RevenueTracker


class TopicRanker:

    def __init__(self):
        self.gate = QualityThresholdGate()
        self.revenue_tracker = RevenueTracker()

    # ==========================================================
    # EXISTING BASE SCORING LOGIC (UNCHANGED CORE WEIGHTS)
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
            "cluster": "ai_future",
            "depth_score": 0.6,
            "curiosity_score": 0.7
        }
        """

        weights = {
            "search_demand": 0.22,
            "emotional_intensity": 0.18,
            "controversy": 0.12,
            "evergreen": 0.18,
            "cluster_fit": 0.15,
            "profit_weight": 0.15   # 🔥 NEW PROFIT INJECTION
        }

        base_score = 0
        for key in [
            "search_demand",
            "emotional_intensity",
            "controversy",
            "evergreen",
            "cluster_fit"
        ]:
            base_score += topic.get(key, 0) * weights[key]

        profit_score = self.get_profit_weight(topic.get("cluster"))

        final_score = (
            base_score +
            (profit_score * weights["profit_weight"])
        )

        return {
            "title": topic["title"],
            "priority_score": round(final_score, 3),
            "depth_score": topic.get("depth_score", 0.5),
            "curiosity_score": topic.get("curiosity_score", 0.5),
            "cluster": topic.get("cluster"),
            "profit_score": profit_score
        }

    # ==========================================================
    # PROFIT WEIGHT CALCULATION
    # ==========================================================

    def get_profit_weight(self, cluster: str) -> float:
        """
        Normalizes RPM per cluster to 0–1 scale.
        """

        if not cluster:
            return 0.5

        summary = self.revenue_tracker.cluster_revenue_summary()

        if not summary:
            return 0.5

        cluster_rpms = {row[0]: row[1] for row in summary if row[1] is not None}

        if not cluster_rpms:
            return 0.5

        max_rpm = max(cluster_rpms.values())
        min_rpm = min(cluster_rpms.values())

        current_rpm = cluster_rpms.get(cluster)

        if current_rpm is None:
            return 0.5

        if max_rpm == min_rpm:
            return 0.5

        # Normalize between 0 and 1
        normalized = (current_rpm - min_rpm) / (max_rpm - min_rpm)

        return round(normalized, 3)

    # ==========================================================
    # RANKING
    # ==========================================================

    def rank(self, topics: List[Dict]) -> List[Dict]:
        scored = [self.score_topic(t) for t in topics]
        return sorted(scored, key=lambda x: x["priority_score"], reverse=True)

    # ==========================================================
    # STRICT QUALITY GATE ENFORCEMENT
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
                f"Score={topic['priority_score']} | "
                f"ProfitScore={topic['profit_score']}"
            )

            return topic

        logging.error("All candidate topics rejected by quality gate.")
        raise Exception("No topics passed quality threshold.")
