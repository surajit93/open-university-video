# scripts/retry_utils.py

import time
import random
import logging
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError

# 🔥 NEW
try:
    from scripts.video_cost_engine import log_api_cost
except Exception:
    def log_api_cost(*args, **kwargs):
        pass


def retry_with_backoff(
    func,
    retries=5,
    base_delay=2,
    exponential=True,
    jitter=True,
    escalate_quota=True,
    api_name=None,
    estimated_cost=0
):
    """
    Production-grade retry wrapper.

    - Exponential backoff
    - Jitter support
    - Quota detection
    - Structured logging
    - 🔥 Cost logging hook
    - 🔥 Sleep-until-reset detection
    """

    for attempt in range(retries):
        try:
            result = func()

            # 🔥 COST HOOK (unchanged behavior)
            if api_name:
                log_api_cost(api_name, estimated_cost)

            return result

        except HttpError as e:
            error_str = str(e)

            if escalate_quota and (
                "quotaExceeded" in error_str
                or "userRateLimitExceeded" in error_str
            ):
                logging.error("[RETRY] Quota exceeded. Attempting reset detection.")

                sleep_seconds = _detect_reset_window(e)

                logging.error(f"[RETRY] Sleeping {sleep_seconds}s until quota reset.")
                time.sleep(sleep_seconds)

                raise

            _sleep(attempt, base_delay, exponential, jitter)

        except Exception:
            if attempt == retries - 1:
                raise

            _sleep(attempt, base_delay, exponential, jitter)


def _detect_reset_window(error):
    """
    Attempts to detect quota reset window from headers.
    Fallback = 1 hour.
    """

    try:
        headers = getattr(error.resp, "headers", {})

        reset_time = headers.get("X-RateLimit-Reset")

        if reset_time:
            reset_timestamp = int(reset_time)
            now_timestamp = int(datetime.utcnow().timestamp())
            delta = max(reset_timestamp - now_timestamp, 0)
            return max(delta, 60)

    except Exception:
        pass

    # Fallback: 1 hour safe window
    return 3600


def _sleep(attempt, base_delay, exponential, jitter):
    delay = base_delay

    if exponential:
        delay *= (2 ** attempt)

    if jitter:
        delay += random.random()

    time.sleep(delay)
