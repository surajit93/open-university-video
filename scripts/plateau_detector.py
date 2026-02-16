import sqlite3
from statistics import mean


class PlateauDetector:

    DB_PATH = "data/performance.db"

    def subscriber_growth_rate(self, window=10):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT returning_viewer_pct
        FROM video_performance
        ORDER BY id DESC
        LIMIT ?
        """, (window,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return 0

        values = [r[0] for r in rows if r[0] is not None]
        return mean(values) if values else 0

    def is_plateau(self, threshold=1.0):
        growth = self.subscriber_growth_rate()
        return growth < threshold
