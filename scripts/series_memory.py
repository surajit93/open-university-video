# scripts/series_memory.py

import sqlite3
from typing import Optional


class SeriesMemory:
    def __init__(self, db_path: str = "data/improvement_history.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS series_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_name TEXT,
            last_video_id TEXT,
            last_hook TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def update(self, series_name: str,
               video_id: str, hook: str):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO series_memory
        (series_name, last_video_id, last_hook)
        VALUES (?, ?, ?)
        """, (series_name, video_id, hook))

        conn.commit()
        conn.close()

    def previous_hook(self, series_name: str) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT last_hook FROM series_memory
        WHERE series_name = ?
        ORDER BY id DESC
        LIMIT 1
        """, (series_name,))

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None
