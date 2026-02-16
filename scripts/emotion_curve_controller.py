#scripts/emotion_curve_controller.py
from statistics import mean


class EmotionCurveController:
    """
    Detect flat emotional segments and force spikes.
    """

    EMOTION_TERMS = [
        "shocking", "dangerous", "terrifying", "massive",
        "critical", "unbelievable", "catastrophic"
    ]

    def segment_score(self, segment: str) -> float:
        lower = segment.lower()
        hits = sum(1 for word in self.EMOTION_TERMS if word in lower)
        return hits / 3

    def analyze(self, script: str, segment_size=120):
        words = script.split()
        segments = [
            " ".join(words[i:i + segment_size])
            for i in range(0, len(words), segment_size)
        ]

        scores = [self.segment_score(seg) for seg in segments]

        if not scores:
            return script

        avg_score = mean(scores)

        # Flatline detection
        if avg_score < 0.2:
            raise Exception("Emotional flatline detected.")

        return script

    def inject_spikes(self, script: str):
        words = script.split()
        for i in range(200, len(words), 200):
            words.insert(i, "This changes everything.")
        return " ".join(words)
