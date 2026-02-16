# scripts/packaging_guard.py

import datetime
import re
import sqlite3
import os
from collections import Counter

COOLING_SECONDS = 86400  # 24 hours
TITLE_DB = "data/title_history.db"


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


# 🔥 NEW – Persistent Title Memory (Additive Only)

def _init_title_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(TITLE_DB)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS title_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


def store_title(title: str):
    _init_title_db()
    conn = sqlite3.connect(TITLE_DB)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO title_history (title, created_at)
    VALUES (?, ?)
    """, (title, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_last_n_titles(n=20):
    _init_title_db()
    conn = sqlite3.connect(TITLE_DB)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT title FROM title_history
    ORDER BY id DESC
    LIMIT ?
    """, (n,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]
