# scripts/first30_validator.py

import re

GREETING_PATTERNS = ["welcome", "today we are going to", "hi everyone"]

PHILOSOPHY_PATTERNS = [
    "why this matters",
    "this affects you",
    "what changes",
    "what this means for you"
]


def contains_greeting(text):
    return any(p in text.lower() for p in GREETING_PATTERNS)


def contains_stakes(text):
    keywords = ["could", "risk", "impact", "threat", "future"]
    return any(k in text.lower() for k in keywords)


def contains_curiosity(text):
    return "?" in text or "what if" in text.lower()


def contains_promise(text):
    keywords = ["in this video", "you will see", "you'll understand"]
    return any(k in text.lower() for k in keywords)


def contains_philosophy_signal(text):
    """
    Enforces: viewer relevance must exist.
    Prevents generic documentary-style drift.
    """
    return any(p in text.lower() for p in PHILOSOPHY_PATTERNS)


def validate_first30(first30_text):
    """
    Structural + psychological enforcement.
    """

    if contains_greeting(first30_text):
        raise Exception("First30 rejected: greeting detected.")

    if not contains_stakes(first30_text):
        raise Exception("First30 rejected: no stakes introduced.")

    if not contains_curiosity(first30_text):
        raise Exception("First30 rejected: no curiosity gap.")

    if not contains_promise(first30_text):
        raise Exception("First30 rejected: no clear promise.")

    # 🔥 NEW — Philosophy enforcement
    if not contains_philosophy_signal(first30_text):
        raise Exception(
            "First30 rejected: missing viewer-relevance philosophy signal."
        )

    return True
