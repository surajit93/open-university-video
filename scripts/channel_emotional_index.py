# scripts/channel_emotional_index.py

import sqlite3


class ChannelEmotionalIndex:

    def __init__(self, db_path="data/improvement_history.db"):
        self.conn = sqlite3.connect(db_path)

    def calculate_index(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT emotion_tag, COUNT(*)
            FROM improvement_history
            GROUP BY emotion_tag
        """)
        data = cursor.fetchall()

        total = sum(count for _, count in data)
        distribution = {
            tag: round(count / total, 2)
            for tag, count in data
        } if total else {}

        return distribution

    def needs_balance(self, threshold=0.6):
        distribution = self.calculate_index()

        for tag, ratio in distribution.items():
            if ratio > threshold:
                return True, f"Emotion over-saturated: {tag}"

        return False, None
