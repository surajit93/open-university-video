# scripts/retry_utils.py

import time
import random
import logging
from googleapiclient.errors import HttpError


def retry_with_backoff(
    func,
    retries=5,
    base_delay=2,
    exponential=True,
    jitter=True,
    escalate_quota=True
):
    """
    Production-grade retry wrapper.

    - Exponential backoff
    - Jitter support
    - Quota detection
    - Structured logging
    """

    for attempt in range(retries):
        try:
            return func()

        except HttpError as e:
            error_str = str(e)

            # Hard stop for quota issues
            if escalate_quota and (
                "quotaExceeded" in error_str
                or "userRateLimitExceeded" in error_str
            ):
                logging.error("[RETRY] Quota exceeded. Escalating.")
                raise

            _sleep(attempt, base_delay, exponential, jitter)

        except Exception as e:
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
