import sqlite3
import datetime
import os
import json
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scripts.youtube_auth import get_authenticated_credentials
from scripts.retry_utils import retry_with_backoff

PERF_DB = "data/performance.db"
IMPROVE_DB = "data/improvement_history.db"
RETENTION_DIR = "data/retention"


# ==============================
# DATABASE INIT
# ==============================

def init_performance_db():
    os.makedirs("data", exist_ok=True)

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


# ==============================
# YOUTUBE ANALYTICS SERVICE
# ==============================

def get_analytics_service():
    creds = get_authenticated_credentials()
    return build("youtubeAnalytics", "v2", credentials=creds)


# ==============================
# METRICS FETCH
# ==============================

def fetch_video_metrics(video_id, start_date, end_date):
    service = get_analytics_service()

    def query():
        return service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,impressions,averageViewDuration,averageViewPercentage,subscribersGained",
            filters=f"video=={video_id}"
        ).execute()

    return retry_with_backoff(query)


# ==============================
# RETENTION CURVE FETCH
# ==============================

def fetch_retention_curve(video_id, start_date, end_date):
    service = get_analytics_service()

    def query():
        return service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="audienceWatchRatio",
            dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id}",
            sort="elapsedVideoTimeRatio"
        ).execute()

    return retry_with_backoff(query)


def store_retention_curve(video_id, data):
    os.makedirs(RETENTION_DIR, exist_ok=True)
    path = os.path.join(RETENTION_DIR, f"{video_id}.json")
    with open(path, "w") as f:
        json.dump(data, f)


def extract_30s_retention(retention_response):
    """
    Extract retention at ~30% timeline.
    elapsedVideoTimeRatio is between 0 and 1.
    """
    if "rows" not in retention_response:
        return None

    for row in retention_response["rows"]:
        timeline_ratio = float(row[0])
        if 0.29 <= timeline_ratio <= 0.31:
            return float(row[1]) * 100

    return None


# ==============================
# VIEWS PER HOUR CALCULATION
# ==============================

def calculate_views_per_hour(views, published_hours=24):
    if published_hours <= 0:
        return 0
    return views / published_hours


# ==============================
# MAIN TRACKING FUNCTION
# ==============================

def track_performance(video_id, published_hours=24):
    init_performance_db()

    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=7)).isoformat()
    end_date = today.isoformat()

    try:
        metrics_response = fetch_video_metrics(video_id, start_date, end_date)
        retention_response = fetch_retention_curve(video_id, start_date, end_date)

        store_retention_curve(video_id, retention_response)

        # Parse metrics
        if "rows" not in metrics_response:
            print("No analytics rows returned.")
            return

        row = metrics_response["rows"][0]

        views = int(row[0])
        impressions = int(row[1])
        avg_view_duration = float(row[2])
        avg_view_pct = float(row[3])
        subscribers_gained = int(row[4])

        ctr = 0
        if impressions > 0:
            ctr = (views / impressions) * 100

        retention_30 = extract_30s_retention(retention_response)
        views_per_hour = calculate_views_per_hour(views, published_hours)

        returning_viewer_pct = 0  # Placeholder until cohort query added

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
            impressions,
            ctr,
            avg_view_duration,
            retention_30,
            views,
            views_per_hour,
            returning_viewer_pct
        ))

        conn.commit()
        conn.close()

        print(f"[PERFORMANCE] Tracked successfully for {video_id}")

    except HttpError as e:
        print(f"[ERROR] YouTube API error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")

def ensure_retention_folder():
    os.makedirs("data/retention", exist_ok=True)

