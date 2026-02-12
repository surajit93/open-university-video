import sqlite3
import datetime

PERF_DB = "data/performance.db"
IMPROVE_DB = "data/improvement_history.db"

def init_performance_db():
    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        date TEXT,
        impressions INTEGER,
        ctr REAL,
        avg_view_duration REAL,
        retention_30 REAL,
        views INTEGER,
        views_per_hour REAL,
        returning_viewer_pct REAL
    )
    """)

    conn.commit()
    conn.close()

def track_performance(video_id="latest_video"):
    init_performance_db()

    # Placeholder for real YouTube API integration
    metrics = {
        "impressions": 10000,
        "ctr": 4.2,
        "avg_view_duration": 210,
        "retention_30": 62,
        "views": 420,
        "views_per_hour": 12,
        "returning_viewer_pct": 18
    }

    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO video_performance (
        video_id, date, impressions, ctr,
        avg_view_duration, retention_30,
        views, views_per_hour, returning_viewer_pct
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        video_id,
        datetime.datetime.now().isoformat(),
        metrics["impressions"],
        metrics["ctr"],
        metrics["avg_view_duration"],
        metrics["retention_30"],
        metrics["views"],
        metrics["views_per_hour"],
        metrics["returning_viewer_pct"]
    ))

    conn.commit()
    conn.close()

    print("Performance tracked.")
