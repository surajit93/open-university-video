# scripts/velocity_monitor.py

import sqlite3
from typing import Dict


class VelocityMonitor:
    def __init__(self, db_path: str = "data/performance.db"):
        self.db_path = db_path

    def get_velocity(self, video_id: str) -> float:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT views_per_hour
        FROM video_performance
        WHERE video_id = ?
        ORDER BY date DESC
        LIMIT 1
        """, (video_id,))

        row = cursor.fetchone()
        conn.close()

        return float(row[0]) if row else 0.0

    def detect_breakout(self, video_id: str, baseline: float = 1.8) -> Dict:
        velocity = self.get_velocity(video_id)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT AVG(views_per_hour)
        FROM video_performance
        """)

        avg_velocity = cursor.fetchone()[0] or 1
        conn.close()

        ratio = velocity / avg_velocity if avg_velocity else 0

        return {
            "velocity": velocity,
            "baseline_avg": avg_velocity,
            "ratio": ratio,
            "is_breakout": ratio >= baseline
        }
