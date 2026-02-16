import time
import logging
from datetime import datetime, timedelta


class QuotaManager:

    def __init__(self):
        self.reset_hour_utc = 0  # default midnight UTC reset

    def is_quota_error(self, error: Exception) -> bool:
        msg = str(error).lower()
        return "quota" in msg or "rate limit" in msg or "exceeded" in msg

    def sleep_until_reset(self):
        now = datetime.utcnow()
        reset_time = now.replace(
            hour=self.reset_hour_utc,
            minute=0,
            second=0,
            microsecond=0
        )

        if now >= reset_time:
            reset_time += timedelta(days=1)

        sleep_seconds = (reset_time - now).total_seconds()

        logging.warning(
            f"[QUOTA] Sleeping until reset ({sleep_seconds:.0f}s)"
        )

        time.sleep(sleep_seconds)

    def handle(self, error: Exception):
        if self.is_quota_error(error):
            self.sleep_until_reset()
            return True
        return False
