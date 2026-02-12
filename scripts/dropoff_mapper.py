# scripts/dropoff_mapper.py

import sqlite3
from typing import Dict


class DropoffMapper:
    def __init__(self, db_path: str = "data/improvement_history.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dropoff_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            drop_second INTEGER,
            scene_type TEXT,
            retention_at_drop REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def store_drop(self, video_id: str, drop_second: int,
                   scene_type: str, retention: float):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO dropoff_patterns
        (video_id, drop_second, scene_type, retention_at_drop)
        VALUES (?, ?, ?, ?)
        """, (video_id, drop_second, scene_type, retention))

        conn.commit()
        conn.close()

    def worst_scene_type(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT scene_type, COUNT(*) as c
        FROM dropoff_patterns
        GROUP BY scene_type
        ORDER BY c DESC
        LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None
