# scripts/revenue_tracker.py

import sqlite3
from datetime import datetime


class RevenueTracker:

    def __init__(self, db_path="data/performance.db"):
        self.conn = sqlite3.connect(db_path)
        self._ensure_table()

    def _ensure_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS revenue_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            cluster TEXT,
            rpm REAL,
            estimated_revenue REAL,
            date TEXT
        )
        """)
        self.conn.commit()

    def record_revenue(self, video_id: str, cluster: str, rpm: float, views: int):
        revenue = (views / 1000.0) * rpm

        self.conn.execute("""
        INSERT INTO revenue_metrics (video_id, cluster, rpm, estimated_revenue, date)
        VALUES (?, ?, ?, ?, ?)
        """, (
            video_id,
            cluster,
            rpm,
            revenue,
            datetime.utcnow().isoformat()
        ))

        self.conn.commit()

    def cluster_revenue_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT cluster, AVG(rpm), SUM(estimated_revenue)
        FROM revenue_metrics
        GROUP BY cluster
        """)
        return cursor.fetchall()
