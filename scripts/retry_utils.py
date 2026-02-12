# scripts/retry_utils.py

import time
import random


def retry_with_backoff(func, retries=5):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = (2 ** attempt) + random.random()
            time.sleep(wait)
