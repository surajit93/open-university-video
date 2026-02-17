# scripts/adaptive_retention_intelligence.py

import re
from typing import List, Dict, Callable


class AdaptiveRetentionIntelligence:
    """
    WAVE 3 – Adaptive Rewrite Intelligence Engine

    Combines:

    1️⃣ Segment-Level Retention Mapping
    2️⃣ Weak Section Targeted Rewriting
    3️⃣ Topic Conviction Validation
    4️⃣ Urgency Enforcement Gate

    Purpose:
    Transform static video production into self-correcting retention system.
    """

    # ============================================================
    # CONFIG
    # ============================================================

    RETENTION_DROP_THRESHOLD = 0.07
    MIN_URGENCY_SCORE = 0.45
    MIN_CONVICTION_SCORE = 0.4

    BRUTALITY_KEYWORDS = [
        "risk", "threat", "collapse", "danger",
        "crisis", "survival", "exposed",
        "decline", "replacement", "war"
    ]

    URGENCY_KEYWORDS = [
        "now", "before", "too late",
        "urgent", "warning", "immediately",
        "happening", "this year", "today"
    ]

    IDENTITY_TERMS = [
        "you", "your", "future", "career",
        "life", "income", "status", "position"
    ]

    # ============================================================
    # INIT
    # ============================================================

    def __init__(self, llm_callable: Callable[[str], str] = None):
        """
        llm_callable is optional.
        Required only if weak section rewriting is enabled.
        """
        self.llm = llm_callable

    # ============================================================
    # 1️⃣ SEGMENT-LEVEL RETENTION MAPPER
    # ============================================================

    def map_drops_to_segments(
        self,
        retention_curve: List[float],
        script: str,
        words_per_segment: int = 120
    ) -> Dict:
        """
        Detects drop indices and maps them to script segments.
        """

        if not retention_curve:
            return {"weak_segments": [], "drop_points": []}

        drop_points = []

        for i in range(1, len(retention_curve)):
            if retention_curve[i - 1] - retention_curve[i] > self.RETENTION_DROP_THRESHOLD:
                drop_points.append(i)

        words = script.split()
        segments = [
            words[i:i + words_per_segment]
            for i in range(0, len(words), words_per_segment)
        ]

        weak_segments = []

        for drop_index in drop_points:
            segment_index = drop_index // 5  # coarse mapping
            if segment_index < len(segments):
                weak_segments.append(segment_index)

        return {
            "weak_segments": sorted(set(weak_segments)),
            "drop_points": drop_points
        }

    # ============================================================
    # 2️⃣ WEAK SECTION REWRITER
    # ============================================================

    def rewrite_weak_sections(
        self,
        script: str,
        weak_segment_indexes: List[int],
        words_per_segment: int = 120
    ) -> str:
        """
        Rewrites only weak segments using LLM.
        """

        if not self.llm:
            return script

        words = script.split()

        segments = [
            words[i:i + words_per_segment]
            for i in range(0, len(words), words_per_segment)
        ]

        for index in weak_segment_indexes:
            if index >= len(segments):
                continue

            original_segment = " ".join(segments[index])

            prompt = f"""
Rewrite this section to:

- Increase tension
- Increase second-person intensity
- Add consequence
- Remove explanation fluff

Section:
{original_segment}
"""

            rewritten = self.llm(prompt)

            segments[index] = rewritten.split()

        return " ".join(word for segment in segments for word in segment)

    # ============================================================
    # 3️⃣ TOPIC CONVICTION ENGINE
    # ============================================================

    def topic_conviction_score(self, title: str) -> float:
        """
        Measures existential stake intensity.
        """

        lower = title.lower()

        brutality_hits = sum(1 for k in self.BRUTALITY_KEYWORDS if k in lower)
        identity_hits = sum(1 for k in self.IDENTITY_TERMS if k in lower)

        brutality_score = brutality_hits / len(self.BRUTALITY_KEYWORDS)
        identity_score = identity_hits / len(self.IDENTITY_TERMS)

        return round(min(brutality_score + identity_score, 1.0), 3)

    # ============================================================
    # 4️⃣ URGENCY VALIDATION GATE
    # ============================================================

    def urgency_score(self, title: str) -> float:
        lower = title.lower()
        hits = sum(1 for k in self.URGENCY_KEYWORDS if k in lower)
        return round(min(hits / len(self.URGENCY_KEYWORDS), 1.0), 3)

    def validate_topic(self, title: str) -> Dict:
        conviction = self.topic_conviction_score(title)
        urgency = self.urgency_score(title)

        approved = (
            conviction >= self.MIN_CONVICTION_SCORE and
            urgency >= self.MIN_URGENCY_SCORE
        )

        return {
            "conviction_score": conviction,
            "urgency_score": urgency,
            "approved": approved
        }

    # ============================================================
    # FULL ADAPTIVE LOOP
    # ============================================================

    def adaptive_refine(
        self,
        title: str,
        script: str,
        retention_curve: List[float]
    ) -> Dict:
        """
        Complete self-improving loop.
        """

        validation = self.validate_topic(title)

        retention_mapping = self.map_drops_to_segments(
            retention_curve,
            script
        )

        weak_segments = retention_mapping["weak_segments"]

        refined_script = self.rewrite_weak_sections(
            script,
            weak_segments
        )

        return {
            "validation": validation,
            "weak_segments": weak_segments,
            "refined_script": refined_script
        }
