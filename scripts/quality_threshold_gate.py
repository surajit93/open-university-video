# scripts/quality_threshold_gate.py

from typing import Dict


class QualityThresholdGate:

    def evaluate(self, topic_score: float,
                 depth_score: float,
                 curiosity_score: float,
                 min_topic: float = 0.55,
                 min_depth: float = 0.5,
                 min_curiosity: float = 0.5) -> Dict:

        reject_reasons = []

        if topic_score < min_topic:
            reject_reasons.append("low_topic_score")

        if depth_score < min_depth:
            reject_reasons.append("low_depth_score")

        if curiosity_score < min_curiosity:
            reject_reasons.append("low_curiosity_score")

        return {
            "approved": len(reject_reasons) == 0,
            "reasons": reject_reasons
        }
