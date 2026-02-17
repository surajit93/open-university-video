# scripts/topic_ranker.py

import logging
from typing import Dict, List

from scripts.quality_threshold_gate import QualityThresholdGate
from scripts.revenue_tracker import RevenueTracker

try:
    from scripts.psychological_hook_engine import PsychologicalHookEngine
except Exception:
    PsychologicalHookEngine = None

try:
    from scripts.viral_dna_engine import ViralDNAEngine
except Exception:
    ViralDNAEngine = None

try:
    from scripts.retention_dominance_engine import RetentionDominanceEngine
except Exception:
    RetentionDominanceEngine = None

# 🔥 NEW – Writing Dominance feedback
try:
    from scripts.writing_dominance_engine import WritingDominanceEngine
except Exception:
    WritingDominanceEngine = None


class TopicRanker:

    def __init__(self):
        self.gate = QualityThresholdGate()
        self.revenue_tracker = RevenueTracker()

        self.psych_engine = PsychologicalHookEngine() if PsychologicalHookEngine else None
        self.viral_engine = ViralDNAEngine() if ViralDNAEngine else None
        self.retention_engine = RetentionDominanceEngine() if RetentionDominanceEngine else None

    def score_topic(self, topic: Dict) -> Dict:

        weights = {
            "search_demand": 0.22,
            "emotional_intensity": 0.18,
            "controversy": 0.12,
            "evergreen": 0.18,
            "cluster_fit": 0.15,
            "profit_weight": 0.15
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

        if self.retention_engine:
            brutality_valid = self.retention_engine.validate_topic_brutality(topic["title"])
            identity_score = self.retention_engine.identity_threat_score(topic["title"])
            packaging_score = self.retention_engine.packaging_score(topic["title"])

            if not brutality_valid:
                final_score *= 0.6

            final_score += (identity_score * 0.2)
            final_score += (packaging_score * 0.3)

        # 🔥 Writing engine identity signal boost
        if WritingDominanceEngine:
            evaluator = WritingDominanceEngine(lambda x: topic["title"])
            id_score = evaluator.second_person_ratio(topic["title"])
            final_score += id_score * 0.2

        if self.psych_engine:
            psych_score = self.psych_engine.score_topic(topic["title"])
            try:
                self.psych_engine.enforce(topic["title"])
            except Exception as e:
                logging.warning(f"[PSYCHOLOGICAL REJECT] {e}")
                final_score *= 0.5
        else:
            psych_score = 0

        if self.viral_engine:
            final_score = self.viral_engine.reweight_topic_score(
                final_score,
                topic["title"]
            )

        return {
            "title": topic["title"],
            "priority_score": round(final_score, 3),
            "depth_score": topic.get("depth_score", 0.5),
            "curiosity_score": topic.get("curiosity_score", 0.5),
            "cluster": topic.get("cluster"),
            "profit_score": profit_score,
            "psych_score": psych_score
        }

    def get_profit_weight(self, cluster: str) -> float:

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

        normalized = (current_rpm - min_rpm) / (max_rpm - min_rpm)

        return round(normalized, 3)

    def rank(self, topics: List[Dict]) -> List[Dict]:
        scored = [self.score_topic(t) for t in topics]
        return sorted(scored, key=lambda x: x["priority_score"], reverse=True)

    def select_top_valid(self, topics: List[Dict]) -> Dict:

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
