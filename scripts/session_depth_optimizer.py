# scripts/session_depth_optimizer.py

import sqlite3


class SessionDepthOptimizer:

    def __init__(self, db_path="data/performance.db"):
        self.db_path = db_path

    def average_session_depth(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT avg_videos_per_session FROM performance
        WHERE avg_videos_per_session IS NOT NULL
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return 0

        values = [r[0] for r in rows]
        return sum(values) / len(values)

    def prioritize_clusters(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT cluster_name, AVG(avg_videos_per_session)
        FROM performance
        GROUP BY cluster_name
        """)

        results = cursor.fetchall()
        conn.close()

        return sorted(results, key=lambda x: x[1] or 0, reverse=True)
