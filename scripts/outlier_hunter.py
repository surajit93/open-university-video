# scripts/outlier_hunter.py

class OutlierHunter:

    def should_trigger_outlier(self, total_uploads: int) -> bool:
        return total_uploads % 10 == 0

    def amplify_topic(self, topic: dict) -> dict:
        """
        Increase tension and ambition level.
        """

        topic["risk_level"] = "high"
        topic["tension_multiplier"] = 1.3
        topic["ambition_mode"] = True

        return topic
