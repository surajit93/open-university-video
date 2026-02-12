# scripts/novelty_detector.py

import sqlite3


class NoveltyDetector:

    def __init__(self, db_path="data/improvement_history.db"):
        self.conn = sqlite3.connect(db_path)

    def check_repetition(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT hook_pattern, COUNT(*)
            FROM improvement_history
            GROUP BY hook_pattern
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """)
        result = cursor.fetchone()

        if result and result[1] >= 5:
            return True, f"Hook pattern overused: {result[0]}"

        return False, None
