# scripts/thumbnail_emotion_variance.py

import sqlite3
from collections import Counter


class ThumbnailEmotionVariance:

    def __init__(self, db_path="data/improvement_history.db"):
        self.db_path = db_path

    def last_emotions(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT thumbnail_emotion
        FROM improvements
        ORDER BY created_at DESC
        LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [r[0] for r in rows if r[0]]

    def enforce_diversity(self):
        emotions = self.last_emotions()
        count = Counter(emotions)

        return {
            "distribution": dict(count),
            "dominant_emotion": count.most_common(1)[0][0] if count else None,
            "needs_variation": any(v >= 4 for v in count.values())
        }
