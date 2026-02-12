# scripts/init_improvement_db.py

import sqlite3

DB_PATH = "data/improvement_history.db"

def init_improvement_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS improvement_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        hook_score REAL,
        depth_score REAL,
        curiosity_score REAL,
        thumbnail_emotion_score REAL,
        retention_slope REAL,
        ctr REAL,
        velocity REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_improvement_db()
