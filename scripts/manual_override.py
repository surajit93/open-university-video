# scripts/manual_override.py

class ManualOverride:

    def __init__(self):
        self.paused = False
        self.reason = None

    def evaluate(self, recent_metrics: list):
        """
        recent_metrics format:
        [
            {"ctr": 2.5, "retention_30s": 25},
            ...
        ]
        """

        low_ctr_count = sum(1 for m in recent_metrics if m["ctr"] < 3)
        low_retention_count = sum(1 for m in recent_metrics if m["retention_30s"] < 30)

        if low_ctr_count >= 5:
            self.paused = True
            self.reason = "CTR below 3% for 5 uploads"

        if low_retention_count >= 5:
            self.paused = True
            self.reason = "Retention below 30% for 5 uploads"

        return self.paused, self.reason
