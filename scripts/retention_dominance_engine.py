import re
from statistics import mean


class RetentionDominanceEngine:
    """
    Unified Psychological + Narrative + Packaging Retention Engine

    Combines:
    - Psychological copy amplification
    - Identity threat scoring
    - Topic brutality validation
    - Curiosity gap enforcement
    - Urgency framing
    - Personal consequence injection
    - Escalation ladder enforcement
    - Rewrite loop reinforcement
    - Dropoff feedback analysis
    - Packaging dominance scoring
    """

    # ============================================================
    # MASSIVE PSYCHOLOGICAL TRIGGER LIBRARY
    # ============================================================

    TRIGGER_PHRASES = [
        # Identity Threat
        "you are already behind",
        "you are not prepared",
        "you are being replaced",
        "you are at risk",
        "your future is uncertain",
        "your advantage is disappearing",
        "your career is vulnerable",
        "your status is fragile",

        # Existential Framing
        "this changes everything",
        "this could end what you know",
        "this will redefine your future",
        "this reshapes your reality",
        "this affects your survival",

        # Urgency
        "before it's too late",
        "this is happening now",
        "you don't have time",
        "you cannot ignore this",
        "you must understand this now",

        # Curiosity Shock
        "you won't see this coming",
        "what happens next will shock you",
        "the real danger is hidden",
        "nobody is talking about this",
        "the truth is worse than you think",

        # Personal Consequence
        "this affects you",
        "this impacts your life",
        "this changes your position",
        "this determines your outcome",
        "this directly concerns you"
    ]

    BRUTAL_TOPIC_KEYWORDS = [
        "risk", "threat", "collapse", "danger", "war",
        "survival", "crisis", "replacement", "failure",
        "hidden", "secret", "exposed", "decline"
    ]

    IDENTITY_TRIGGERS = [
        "you", "your", "future", "career", "life",
        "family", "position", "status", "income"
    ]

    PACKAGING_POWER_WORDS = [
        "secret", "danger", "risk", "collapse",
        "hidden", "truth", "warning", "exposed",
        "before", "now"
    ]

    # ============================================================
    # SCRIPT AMPLIFICATION
    # ============================================================

    def amplify_script(self, script: str) -> str:
        """
        Ensure script contains psychological pressure.
        Inject if missing.
        """

        lower = script.lower()

        if not any(p in lower for p in self.TRIGGER_PHRASES):
            script += "\n\nThis directly affects your future."

        if script.lower().count("you") < 6:
            script += "\n\nAsk yourself where you stand in this."

        return script

    # ============================================================
    # ESCALATION LADDER
    # ============================================================

    def enforce_escalation(self, segments: list) -> list:
        """
        Each segment increases tension intensity.
        """

        escalated = []
        intensity = 1

        for seg in segments:
            seg["tension_level"] = intensity
            seg["amplification_note"] = f"Tension stage {intensity}"
            intensity += 1
            escalated.append(seg)

        return escalated

    # ============================================================
    # REWRITE LOOP
    # ============================================================

    def rewrite_until_personal(self, script: str, min_mentions=8) -> str:
        """
        Enforce second-person dominance.
        """

        while script.lower().count("you") < min_mentions:
            script += "\n\nThis changes your trajectory."

        return script

    # ============================================================
    # DROPOFF ANALYSIS
    # ============================================================

    def detect_weak_points(self, retention_curve: list) -> list:
        weak = []
        for i in range(1, len(retention_curve)):
            if retention_curve[i-1] - retention_curve[i] > 0.07:
                weak.append(i)
        return weak

    # ============================================================
    # TOPIC BRUTALITY FILTER
    # ============================================================

    def validate_topic_brutality(self, title: str) -> bool:
        return any(k in title.lower() for k in self.BRUTAL_TOPIC_KEYWORDS)

    # ============================================================
    # IDENTITY THREAT SCORE
    # ============================================================

    def identity_threat_score(self, title: str) -> float:
        count = sum(1 for t in self.IDENTITY_TRIGGERS if t in title.lower())
        return min(count / len(self.IDENTITY_TRIGGERS), 1.0)

    # ============================================================
    # CURIOSITY GAP ENFORCEMENT
    # ============================================================

    def enforce_curiosity_gap(self, title: str) -> str:
        if "?" not in title:
            return title + " - What Happens Next?"
        return title

    # ============================================================
    # URGENCY INJECTION
    # ============================================================

    def inject_urgency(self, title: str) -> str:
        if not any(w in title.lower() for w in ["now", "before"]):
            return "Before It's Too Late: " + title
        return title

    # ============================================================
    # PACKAGING DOMINANCE SCORE
    # ============================================================

    def packaging_score(self, title: str) -> float:
        score = 0

        if "?" in title:
            score += 0.25

        if any(w in title.lower() for w in self.PACKAGING_POWER_WORDS):
            score += 0.4

        if "you" in title.lower():
            score += 0.35

        return round(min(score, 1.0), 3)
