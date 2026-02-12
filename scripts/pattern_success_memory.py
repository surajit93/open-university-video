# scripts/pattern_success_memory.py

import sqlite3
from typing import Dict


class PatternSuccessMemory:
    def __init__(self, db_path: str = "data/improvement_history.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pattern_success (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            hook_type TEXT,
            thumbnail_style TEXT,
            emotional_tone TEXT,
            twist_position REAL,
            ctr REAL,
            retention_30 REAL,
            velocity_48h REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def store(self, data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO pattern_success
        (video_id, hook_type, thumbnail_style, emotional_tone,
         twist_position, ctr, retention_30, velocity_48h)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["video_id"],
            data["hook_type"],
            data["thumbnail_style"],
            data["emotional_tone"],
            data["twist_position"],
            data["ctr"],
            data["retention_30"],
            data["velocity_48h"]
        ))

        conn.commit()
        conn.close()

    def best_hook_type(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT hook_type, AVG(retention_30)
        FROM pattern_success
        GROUP BY hook_type
        ORDER BY AVG(retention_30) DESC
        LIMIT 1
        """)

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None
