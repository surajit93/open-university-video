# scripts/retry_utils.py

import time
import random
import logging
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
    """

    for attempt in range(retries):
        try:
            result = func()

            # 🔥 COST HOOK
            if api_name:
                log_api_cost(api_name, estimated_cost)

            return result

        except HttpError as e:
            error_str = str(e)

            # 🔥 QUOTA ESCALATION (SLEEP UNTIL RESET APPROX)
            if escalate_quota and (
                "quotaExceeded" in error_str
                or "userRateLimitExceeded" in error_str
            ):
                logging.error("[RETRY] Quota exceeded. Escalating sleep.")

                # Sleep 1 hour as safe reset buffer
                time.sleep(3600)
                raise

            _sleep(attempt, base_delay, exponential, jitter)

        except Exception:
            if attempt == retries - 1:
                raise

            _sleep(attempt, base_delay, exponential, jitter)


def _sleep(attempt, base_delay, exponential, jitter):
    delay = base_delay

    if exponential:
        delay *= (2 ** attempt)

    if jitter:
        delay += random.random()

    time.sleep(delay)
