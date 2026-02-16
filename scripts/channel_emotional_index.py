# scripts/channel_emotional_index.py

import sqlite3


class ChannelEmotionalIndex:

    def __init__(self, db_path="data/improvement_history.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS improvement_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            emotion_tag TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def log_emotion(self, video_id: str, emotion_tag: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO improvement_history (video_id, emotion_tag)
        VALUES (?, ?)
        """, (video_id, emotion_tag))

        conn.commit()
        conn.close()

    def calculate_index(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT emotion_tag, COUNT(*)
            FROM improvement_history
            GROUP BY emotion_tag
        """)

        data = cursor.fetchall()
        conn.close()

        total = sum(count for _, count in data)

        if not total:
            return {}

        return {
            tag: round(count / total, 3)
            for tag, count in data
        }

    def governance_signal(self, threshold=0.6):
        """
        Returns:
        {
            "over_saturated": bool,
            "dominant_emotion": str or None,
            "ratio": float
        }
        """
        distribution = self.calculate_index()

        if not distribution:
            return {
                "over_saturated": False,
                "dominant_emotion": None,
                "ratio": 0
            }

        dominant = max(distribution.items(), key=lambda x: x[1])
        emotion, ratio = dominant

        if ratio >= threshold:
            return {
                "over_saturated": True,
                "dominant_emotion": emotion,
                "ratio": ratio
            }

        return {
            "over_saturated": False,
            "dominant_emotion": emotion,
            "ratio": ratio
        }
