# scripts/packaging_guard.py

import datetime
import re
from collections import Counter

COOLING_SECONDS = 86400  # 24 hours


def enforce_cooling_period(created_timestamp):
    """
    created_timestamp must be datetime object
    """
    now = datetime.datetime.now()
    delta = (now - created_timestamp).total_seconds()

    if delta < COOLING_SECONDS:
        remaining = COOLING_SECONDS - delta
        raise RuntimeError(
            f"Packaging cooling active. {remaining/3600:.2f} hours remaining."
        )


# 🔥 NEW – ENTROPY GUARD

def enforce_entropy_guard(title_history: list, new_title: str, threshold=0.75):
    """
    Prevent repetitive title structures.
    Basic lexical similarity entropy guard.
    """

    if not title_history:
        return True

    def tokenize(text):
        return set(re.findall(r"\w+", text.lower()))

    new_tokens = tokenize(new_title)

    similarities = []

    for old in title_history:
        old_tokens = tokenize(old)
        if not old_tokens:
            continue

        overlap = len(new_tokens & old_tokens)
        similarity = overlap / max(len(new_tokens), 1)
        similarities.append(similarity)

    if similarities and max(similarities) > threshold:
        raise RuntimeError("Packaging entropy violation: title too similar.")

    return True
