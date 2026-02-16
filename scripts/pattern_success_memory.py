# scripts/pattern_success_memory.py

import sqlite3
from typing import Dict, Optional


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
            velocity REAL,
            weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    # ======================================================
    # STORE SNAPSHOT
    # ======================================================

    def store(self, data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO pattern_success
        (video_id, hook_type, thumbnail_style,
         emotional_tone, twist_position,
         ctr, retention_30, velocity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["video_id"],
            data["hook_type"],
            data["thumbnail_style"],
            data["emotional_tone"],
            data["twist_position"],
            data["ctr"],
            data["retention_30"],
            data["velocity"]
        ))

        conn.commit()
        conn.close()

    # ======================================================
    # BOOST / PENALIZE
    # ======================================================

    def boost_recent_pattern(self, video_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE pattern_success
        SET weight = weight + 0.5
        WHERE video_id = ?
        """, (video_id,))

        conn.commit()
        conn.close()

    def penalize_recent_pattern(self, video_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE pattern_success
        SET weight = weight - 0.3
        WHERE video_id = ?
        """, (video_id,))

        conn.commit()
        conn.close()

    def penalize_emotion(self, emotion: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE pattern_success
        SET weight = weight - 0.2
        WHERE emotional_tone = ?
        """, (emotion,))

        conn.commit()
        conn.close()

    def penalize_hook_structure(self, video_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE pattern_success
        SET weight = weight - 0.4
        WHERE video_id = ?
        """, (video_id,))

        conn.commit()
        conn.close()

    # ======================================================
    # INSIGHT METHODS
    # ======================================================

    def best_hook_type(self) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT hook_type,
               AVG(retention_30 * weight)
        FROM pattern_success
        GROUP BY hook_type
        ORDER BY AVG(retention_30 * weight) DESC
        LIMIT 1
        """)

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def best_thumbnail_style(self) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT thumbnail_style,
               AVG(ctr * weight)
        FROM pattern_success
        GROUP BY thumbnail_style
        ORDER BY AVG(ctr * weight) DESC
        LIMIT 1
        """)

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None
