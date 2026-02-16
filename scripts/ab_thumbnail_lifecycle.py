import os
import json
import logging
import datetime
import sqlite3


class ABThumbnailLifecycle:

    DB_PATH = "data/improvement_history.db"
    THUMB_LOG = "data/thumbnail_ab_log.json"

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thumbnail_winners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            winning_path TEXT,
            decided_at TEXT
        )
        """)
        conn.commit()
        conn.close()

    def register_variants(self, video_id: str, variants: list):
        data = {
            "video_id": video_id,
            "variants": variants,
            "created_at": datetime.datetime.utcnow().isoformat()
        }

        with open(self.THUMB_LOG, "w") as f:
            json.dump(data, f)

    def should_evaluate(self, created_at: str) -> bool:
        created = datetime.datetime.fromisoformat(created_at)
        return (datetime.datetime.utcnow() - created).total_seconds() >= 86400

    def persist_winner(self, video_id: str, winning_path: str):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO thumbnail_winners (video_id, winning_path, decided_at)
        VALUES (?, ?, ?)
        """, (
            video_id,
            winning_path,
            datetime.datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
        logging.info(f"[AB] Winner persisted: {winning_path}")
