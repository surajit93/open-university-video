# scripts/render_benchmark.py

import time
import sqlite3
import os
import datetime

DB = "data/render_benchmark.db"


def init_render_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS render_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            scene_name TEXT,
            render_time REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def benchmark_render(video_id, scene_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            init_render_db()
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start

            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("""
                INSERT INTO render_stats
                (video_id, scene_name, render_time, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                video_id,
                scene_name,
                duration,
                datetime.datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()

            return result
        return wrapper
    return decorator
