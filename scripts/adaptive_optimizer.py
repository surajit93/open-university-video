import sqlite3
import logging
from statistics import mean

from scripts.velocity_monitor import VelocityMonitor
from scripts.pattern_success_memory import PatternSuccessMemory
from scripts.runway_guard import check_runway
from config_loader import load_growth_plan

# 🔥 NEW: Plateau detection integration
try:
    from scripts.plateau_detector import detect_plateau
except Exception:
    def detect_plateau(*args, **kwargs):
        return {"plateau": False}

PERF_DB = "data/performance.db"
IMPROVE_DB = "data/improvement_history.db"


# ============================================================
# HELPERS
# ============================================================

def get_last_n(n=5):
    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ctr, retention_30, views_per_hour
    FROM video_performance
    ORDER BY id DESC
    LIMIT ?
    """, (n,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# 🔥 NEW: Subscriber growth fetch
def get_last_n_subscribers(n=10):
    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT subscribers_gained
        FROM video_performance
        ORDER BY id DESC
        LIMIT ?
        """, (n,))
        rows = cursor.fetchall()
    except Exception:
        rows = []

    conn.close()
    return [r[0] for r in rows if r and r[0] is not None]


# 🔥 NEW: Stronger flatten detection (additive only)
def detect_flatten_trend(values, tolerance=0.1):
    if len(values) < 5:
        return False

    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]

    avg_first = mean(first_half)
    avg_second = mean(second_half)

    if avg_first == 0:
        return False

    change_ratio = abs(avg_second - avg_first) / avg_first

    return change_ratio < tolerance


def get_latest_video_metrics(video_id):
    conn = sqlite3.connect(PERF_DB)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT ctr, retention_30, views_per_hour
    FROM video_performance
    WHERE video_id = ?
    ORDER BY id DESC
    LIMIT 1
    """, (video_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "ctr": row[0] or 0,
        "retention_30": row[1] or 0,
        "velocity": row[2] or 0
    }


def log_breakout_event(video_id, ratio):
    conn = sqlite3.connect(IMPROVE_DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS breakout_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        breakout_ratio REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    INSERT INTO breakout_events (video_id, breakout_ratio)
    VALUES (?, ?)
    """, (video_id, ratio))

    conn.commit()
    conn.close()


# ============================================================
# MAIN ENGINE
# ============================================================

def run_adaptive_optimization(video_id, saturated_emotion=None):

    logging.info("========== ADAPTIVE OPTIMIZATION START ==========")

    growth_plan = load_growth_plan()
    allow_pivot = check_runway(growth_plan)

    rows = get_last_n(growth_plan.get("optimization_window", 5))

    if not rows:
        logging.warning("Not enough data for adaptive optimization.")
        return

    avg_ctr = mean(r[0] for r in rows if r[0] is not None)
    avg_retention = mean(r[1] for r in rows if r[1] is not None)
    avg_velocity = mean(r[2] for r in rows if r[2] is not None)

    logging.info(
        f"[WINDOW AVG] CTR={avg_ctr:.2f} | "
        f"Retention={avg_retention:.2f} | "
        f"Velocity={avg_velocity:.2f}"
    )

    pattern_memory = PatternSuccessMemory()
    velocity_monitor = VelocityMonitor()

    latest_metrics = get_latest_video_metrics(video_id)
    breakout_data = velocity_monitor.detect_breakout(video_id)

    if latest_metrics:
        pattern_memory.store({
            "video_id": video_id,
            "hook_type": "default_hook",
            "thumbnail_style": "dark_centered",
            "emotional_tone": saturated_emotion or "neutral",
            "twist_position": 0.6,
            "ctr": latest_metrics["ctr"],
            "retention_30": latest_metrics["retention_30"],
            "velocity": latest_metrics["velocity"]
        })

    # 🔥 Subscriber plateau detection (additive only)
    subs = get_last_n_subscribers(10)

    if len(subs) >= 5:
        plateau_signal = detect_plateau(subs)
        flatten_signal = detect_flatten_trend(subs)

        if plateau_signal.get("plateau") or flatten_signal:
            logging.warning("[PLATEAU DETECTED] Subscriber growth flattening.")
            pattern_memory.penalize_recent_pattern(video_id)

    # --- ORIGINAL LOGIC BELOW REMAINS UNCHANGED ---

    if breakout_data["is_breakout"]:
        logging.warning(
            f"[BREAKOUT DETECTED] Ratio={breakout_data['ratio']:.2f}"
        )
        log_breakout_event(video_id, breakout_data["ratio"])
        pattern_memory.boost_recent_pattern(video_id)
        logging.info("[ACTION] Boosting cluster + follow-up priority.")

    if avg_ctr < 4:
        logging.warning("[CTR LOW] Thumbnail regeneration required.")
        pattern_memory.penalize_recent_pattern(video_id)

    if avg_retention < 40:
        logging.warning("[RETENTION LOW] Hook structure penalty applied.")
        pattern_memory.penalize_hook_structure(video_id)

    if allow_pivot and avg_velocity < 5:
        logging.warning(
            "[RUNWAY COMPLETE + FLAT VELOCITY] Angle shift recommended."
        )
        pattern_memory.penalize_recent_pattern(video_id)

    if avg_velocity > 20:
        logging.info("[STRONG MOMENTUM] Boost cluster priority.")
        pattern_memory.boost_recent_pattern(video_id)

    if saturated_emotion:
        logging.warning(
            f"[EMOTION GOVERNANCE] Penalizing saturated: {saturated_emotion}"
        )
        pattern_memory.penalize_emotion(saturated_emotion)

    if breakout_data["ratio"] < 0.8:
        logging.info("[UNDERPERFORMING] Penalizing structural pattern.")
        pattern_memory.penalize_recent_pattern(video_id)

    logging.info("========== ADAPTIVE OPTIMIZATION COMPLETE ==========")
