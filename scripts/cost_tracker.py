# scripts/cost_tracker.py

import sqlite3
import datetime
import os

DB_PATH = "data/cost_tracking.db"


def init_cost_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS cost_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            date TEXT,
            service TEXT,
            units REAL,
            cost REAL
        )
    """)

    conn.commit()
    conn.close()


def log_cost(video_id, service, units, cost):
    init_cost_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO cost_tracking (
            video_id, date, service, units, cost
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        video_id,
        datetime.datetime.now().isoformat(),
        service,
        units,
        cost
    ))

    conn.commit()
    conn.close()


def get_total_cost(video_id=None):
    init_cost_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if video_id:
        c.execute("SELECT SUM(cost) FROM cost_tracking WHERE video_id=?", (video_id,))
    else:
        c.execute("SELECT SUM(cost) FROM cost_tracking")

    result = c.fetchone()[0]
    conn.close()
    return result or 0.0
