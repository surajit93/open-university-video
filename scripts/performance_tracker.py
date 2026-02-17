# scripts/performance_tracker.py
import sqlite3
import datetime
import os
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from scripts.youtube_auth import get_authenticated_credentials
from scripts.retry_utils import retry_with_backoff
from scripts.analytics_lock import enforce_analytics_lock
from scripts.dropoff_mapper import DropoffMapper

# 🔥 Optional cost logging (safe fallback if not present)
try:
    from scripts.video_cost_engine import log_api_cost
except Exception:
    def log_api_cost(*args, **kwargs):
        pass

# 🔥 NEW – Adaptive Retention Intelligence (additive only)
try:
    from scripts.adaptive_retention_intelligence import AdaptiveRetentionIntelligence
except Exception:
    AdaptiveRetentionIntelligence = None


PERF_DB = "data/performance.db"
RETENTION_DIR = "data/retention"


# =====================================================
# DATABASE INIT
# =====================================================

def init_performance_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()

    # Preserve original columns
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
        returning_viewer_pct REAL,
        subscribers_gained INTEGER,
        subs_per_1000_views REAL
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# ANALYTICS SERVICE (RETRY SAFE)
# =====================================================

def get_analytics_service():
    def build_service():
        creds = get_authenticated_credentials()
        return build("youtubeAnalytics", "v2", credentials=creds)

    return retry_with_backoff(build_service)


# =====================================================
# METRICS FETCH
# =====================================================

def fetch_video_metrics(video_id, start_date, end_date):
    service = get_analytics_service()

    return retry_with_backoff(
        lambda: service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,impressions,averageViewDuration,averageViewPercentage,subscribersGained",
            filters=f"video=={video_id}"
        ).execute()
    )


def fetch_retention_curve(video_id, start_date, end_date):
    service = get_analytics_service()

    return retry_with_backoff(
        lambda: service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="audienceWatchRatio",
            dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id}",
            sort="elapsedVideoTimeRatio"
        ).execute()
    )


# =====================================================
# RETENTION HANDLING (UNCHANGED)
# =====================================================

def ensure_retention_folder():
    os.makedirs(RETENTION_DIR, exist_ok=True)


def store_retention_curve(video_id, data):
    ensure_retention_folder()

    with open(os.path.join(RETENTION_DIR, f"{video_id}.json"), "w") as f:
        json.dump(data, f)


def extract_30s_retention(retention_response):
    if "rows" not in retention_response:
        return None

    for row in retention_response["rows"]:
        timeline_ratio = float(row[0])
        if 0.29 <= timeline_ratio <= 0.31:
            return float(row[1]) * 100

    return None


def detect_major_drop(retention_response):
    if "rows" not in retention_response:
        return None, None, None

    rows = retention_response["rows"]

    biggest_delta = 0
    drop_second = None
    drop_retention = None

    prev = None

    for row in rows:
        timeline_ratio = float(row[0])
        retention_value = float(row[1])

        if prev is not None:
            delta = prev - retention_value
            if delta > biggest_delta:
                biggest_delta = delta
                drop_second = int(timeline_ratio * 600)
                drop_retention = retention_value * 100

        prev = retention_value

    return drop_second, drop_retention, biggest_delta


def infer_scene_type(second):
    if second is None:
        return None

    if second < 30:
        return "hook"
    elif second < 120:
        return "early_explanation"
    elif second < 300:
        return "mid_body"
    else:
        return "late_section"


def calculate_views_per_hour(views, published_hours=24):
    if published_hours <= 0:
        return 0
    return views / published_hours


# =====================================================
# MAIN TRACKER
# =====================================================

def track_performance(video_id, published_hours=24, force=False):

    # 🔒 Analytics lock discipline (UNCHANGED)
    if not force:
        enforce_analytics_lock()

    init_performance_db()

    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=7)).isoformat()
    end_date = today.isoformat()

    try:
        metrics_response = fetch_video_metrics(video_id, start_date, end_date)
        retention_response = fetch_retention_curve(video_id, start_date, end_date)

        # Cost logging (non-blocking)
        log_api_cost("youtube_analytics_call", 0.001)

        store_retention_curve(video_id, retention_response)

        if "rows" not in metrics_response:
            print("No analytics rows returned.")
            return

        row = metrics_response["rows"][0]

        views = int(row[0])
        impressions = int(row[1])
        avg_view_duration = float(row[2])
        subscribers_gained = int(row[4])

        ctr = (views / impressions) * 100 if impressions else 0
        retention_30 = extract_30s_retention(retention_response)
        views_per_hour = calculate_views_per_hour(views, published_hours)

        returning_viewer_pct = 0

        subs_per_1000_views = (
            (subscribers_gained / views) * 1000 if views else 0
        )

        # --------------------------------------------------
        # STORE METRICS (EXTENDED BUT NOT ALTERED)
        # --------------------------------------------------

        conn = sqlite3.connect(PERF_DB)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO video_performance (
            video_id, date, impressions, ctr,
            avg_view_duration, retention_30,
            views, views_per_hour, returning_viewer_pct,
            subscribers_gained, subs_per_1000_views
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            datetime.datetime.now().isoformat(),
            impressions,
            ctr,
            avg_view_duration,
            retention_30,
            views,
            views_per_hour,
            returning_viewer_pct,
            subscribers_gained,
            subs_per_1000_views
        ))

        conn.commit()
        conn.close()

        # --------------------------------------------------
        # 🔥 AUTO DROP MAPPING (UNCHANGED)
        # --------------------------------------------------

        drop_second, drop_retention, severity = detect_major_drop(retention_response)

        if drop_second is not None:
            scene_type = infer_scene_type(drop_second)

            mapper = DropoffMapper()
            mapper.store_drop(
                video_id=video_id,
                drop_second=drop_second,
                scene_type=scene_type,
                retention=drop_retention,
                severity_score=severity
            )

        # --------------------------------------------------
        # 🔥 NEW – Adaptive Retention Intelligence Hook
        # (Additive only – no regression risk)
        # --------------------------------------------------

        if AdaptiveRetentionIntelligence and "rows" in retention_response:
            try:
                retention_curve = [
                    float(row[1]) for row in retention_response["rows"]
                ]

                # Script may not always exist at this stage – safe fallback
                script_path = "script.txt"
                if os.path.exists(script_path):
                    with open(script_path, "r", encoding="utf-8") as f:
                        script_content = f.read()
                else:
                    script_content = ""

                ari = AdaptiveRetentionIntelligence()

                mapping = ari.map_drops_to_segments(
                    retention_curve=retention_curve,
                    script=script_content
                )

                if mapping["weak_segments"]:
                    print(
                        f"[ADAPTIVE RETENTION] Weak segments detected: "
                        f"{mapping['weak_segments']}"
                    )

            except Exception as e:
                print(f"[ADAPTIVE RETENTION ERROR] {e}")

        print(f"[PERFORMANCE] Full tracking complete for {video_id}")

    except HttpError as e:
        print(f"[ERROR] YouTube API error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
