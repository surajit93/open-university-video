import sqlite3
from datetime import datetime


class VideoCostEngine:

    DB_PATH = "data/cost_tracking.db"

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            openai_cost REAL,
            tts_cost REAL,
            youtube_quota_units REAL,
            total_cost REAL,
            created_at TEXT
        )
        """)
        conn.commit()
        conn.close()

    def record(self, video_id: str,
               openai_cost: float = 0.0,
               tts_cost: float = 0.0,
               youtube_quota_units: float = 0.0):

        total = openai_cost + tts_cost

        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO video_costs
        (video_id, openai_cost, tts_cost,
         youtube_quota_units, total_cost, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            openai_cost,
            tts_cost,
            youtube_quota_units,
            total,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
