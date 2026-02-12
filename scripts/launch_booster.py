# scripts/launch_booster.py

from datetime import datetime


class LaunchBooster:

    def optimal_publish_window(self, config: dict) -> Dict:
        """
        config from channel_config.yaml:
        {
            "upload_days": ["Tue", "Fri"],
            "upload_time": "18:00"
        }
        """

        today = datetime.utcnow().strftime("%a")
        scheduled = today in config.get("upload_days", [])

        return {
            "today_allowed": scheduled,
            "scheduled_time": config.get("upload_time")
        }

    def generate_pinned_comment(self, topic: str) -> str:
        return f"What’s your take on this scenario? Drop your thoughts below 👇 ({topic})"

    def engagement_trigger_question(self, script_summary: str) -> str:
        return f"If this happens, how would it affect you personally?"
