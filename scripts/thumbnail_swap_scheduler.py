#scripts/thumbnail_swap_scheduler.py
import sqlite3
import datetime
import os
from scripts.thumbnail_renderer import render_thumbnail

# 🔥 NEW
try:
    from scripts.pattern_success_memory import PatternSuccessMemory
except Exception:
    PatternSuccessMemory = None

# 🔥 NEW: Real YouTube upload integration (additive only)
try:
    from scripts.youtube_upload import upload_thumbnail
except Exception:
    def upload_thumbnail(*args, **kwargs):
        print("[THUMBNAIL] Upload function not available.")

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
            swapped INTEGER DEFAULT 0,
            winner_thumbnail TEXT
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
        VALUES (?, ?, ?, ?, 0, NULL)
    """, (video_id, scheduled_time, original, alternate))

    conn.commit()
    conn.close()


def execute_due_swaps(performance_lookup_fn):

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

        winner = original

        if ctr < 0.04:
            print(f"Swapping thumbnail for {video_id}")
            winner = alternate

        # 🔥 NEW: Actual upload execution (additive only)
        try:
            upload_thumbnail(video_id, winner)
        except Exception as e:
            print(f"[THUMBNAIL UPLOAD ERROR] {e}")

        # 🔥 NEW: Winner persistence
        c.execute("""
            UPDATE thumbnail_swap_queue
            SET swapped=1, winner_thumbnail=?
            WHERE video_id=?
        """, (winner, video_id))

        # 🔥 NEW: Pattern memory update
        if PatternSuccessMemory:
            pm = PatternSuccessMemory()
            pm.store({
                "video_id": video_id,
                "thumbnail_winner": winner
            })

    conn.commit()
    conn.close()
