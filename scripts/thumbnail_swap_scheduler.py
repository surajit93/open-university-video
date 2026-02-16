# scripts/thumbnail_swap_scheduler.py

import sqlite3
import datetime
import os
from scripts.thumbnail_renderer import render_thumbnail

DB = "data/thumbnail_swaps.db"


def init_swap_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS thumbnail_swap_queue (
            video_id TEXT,
            scheduled_time TEXT,
            original_thumbnail TEXT,
            alternate_thumbnail TEXT,
            swapped INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def schedule_thumbnail_swap(video_id, original, alternate):
    init_swap_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    scheduled_time = (
        datetime.datetime.now() + datetime.timedelta(hours=24)
    ).isoformat()

    c.execute("""
        INSERT INTO thumbnail_swap_queue
        VALUES (?, ?, ?, ?, 0)
    """, (video_id, scheduled_time, original, alternate))

    conn.commit()
    conn.close()


def execute_due_swaps(performance_lookup_fn):
    """
    performance_lookup_fn(video_id) -> returns ctr
    """

    init_swap_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    now = datetime.datetime.now().isoformat()

    c.execute("""
        SELECT video_id, original_thumbnail, alternate_thumbnail
        FROM thumbnail_swap_queue
        WHERE swapped=0 AND scheduled_time <= ?
    """, (now,))

    rows = c.fetchall()

    for video_id, original, alternate in rows:
        ctr = performance_lookup_fn(video_id)

        if ctr < 0.04:  # 4% threshold
            # Replace thumbnail via YouTube API (implement separately)
            print(f"Swapping thumbnail for {video_id}")
            # upload_thumbnail(video_id, alternate)

        c.execute("""
            UPDATE thumbnail_swap_queue
            SET swapped=1
            WHERE video_id=?
        """, (video_id,))

    conn.commit()
    conn.close()
