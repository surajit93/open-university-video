# scripts/adaptive_optimizer.py
import sqlite3
import logging
import os
import json
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

# 🔥 NEW: Retention Dominance Engine (additive only)
try:
    from scripts.retention_dominance_engine import RetentionDominanceEngine
except Exception:
    RetentionDominanceEngine = None

# 🔥 NEW: Adaptive Retention Intelligence (additive only)
try:
    from scripts.adaptive_retention_intelligence import AdaptiveRetentionIntelligence
except Exception:
    AdaptiveRetentionIntelligence = None


PERF_DB = "data/performance.db"
IMPROVE_DB = "data/improvement_history.db"

# 🔥 NEW – Topic context awareness (additive only)
CURRENT_TOPIC_FILE = "current_topic.json"


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


# 🔥 NEW – Topic metadata loader (additive only)
def load_current_topic():
    if not os.path.exists(CURRENT_TOPIC_FILE):
        return {}

    try:
        with open(CURRENT_TOPIC_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


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

    # 🔥 NEW – Topic awareness integration (additive only)
    topic_meta = load_current_topic()
    addiction_score = topic_meta.get("addiction_score", 0.5)
    playlist_cluster = topic_meta.get("playlist_cluster")
    sequel_chain_id = topic_meta.get("sequel_chain_id")
    retention_type = topic_meta.get("retention_type")

    if latest_metrics:
        pattern_memory.store({
            "video_id": video_id,
            "hook_type": "default_hook",
            "thumbnail_style": topic_meta.get("thumbnail_color_strategy", "dark_centered"),
            "emotional_tone": saturated_emotion or topic_meta.get("primary_persona", "neutral"),
            "twist_position": 0.6,
            "ctr": latest_metrics["ctr"],
            "retention_30": latest_metrics["retention_30"],
            "velocity": latest_metrics["velocity"],
            # 🔥 NEW metadata awareness
            "addiction_score": addiction_score,
            "playlist_cluster": playlist_cluster,
            "retention_type": retention_type
        })

    # 🔥 Subscriber plateau detection (unchanged logic preserved)
    subs = get_last_n_subscribers(10)

    if len(subs) >= 5:
        plateau_signal = detect_plateau(subs)
        flatten_signal = detect_flatten_trend(subs)

        if plateau_signal.get("plateau") or flatten_signal:
            logging.warning("[PLATEAU DETECTED] Subscriber growth flattening.")
            pattern_memory.penalize_recent_pattern(video_id)

    # 🔥 Retention Dominance Engine (unchanged logic preserved)
    if RetentionDominanceEngine and latest_metrics:
        try:
            retention_engine = RetentionDominanceEngine()

            synthetic_curve = [
                avg_retention,
                max(avg_retention - 5, 0),
                max(avg_retention - 12, 0)
            ]

            weak_points = retention_engine.detect_weak_points(synthetic_curve)

            if weak_points:
                logging.warning(
                    f"[RETENTION WEAK POINTS DETECTED] Indices: {weak_points}"
                )

        except Exception as e:
            logging.warning(f"[RETENTION ENGINE ERROR] {e}")

    # 🔥 Adaptive Retention Intelligence (unchanged logic preserved)
    if AdaptiveRetentionIntelligence:
        try:
            ari = AdaptiveRetentionIntelligence()

            synthetic_curve = [
                avg_retention / 100 if avg_retention else 0.5,
                max((avg_retention - 5) / 100, 0),
                max((avg_retention - 12) / 100, 0)
            ]

            validation = ari.validate_topic(f"Video {video_id}")

            mapping = ari.map_drops_to_segments(
                retention_curve=synthetic_curve,
                script=""
            )

            if not validation["approved"]:
                logging.warning(
                    f"[ADAPTIVE VALIDATION FAIL] "
                    f"Conviction={validation['conviction_score']} | "
                    f"Urgency={validation['urgency_score']}"
                )

            if mapping["weak_segments"]:
                logging.warning(
                    f"[ADAPTIVE WEAK SEGMENTS DETECTED] "
                    f"{mapping['weak_segments']}"
                )

        except Exception as e:
            logging.warning(f"[ADAPTIVE RETENTION ERROR] {e}")

    # ============================================================
    # ORIGINAL LOGIC BELOW REMAINS UNCHANGED
    # ============================================================

    if breakout_data["is_breakout"]:
        logging.warning(
            f"[BREAKOUT DETECTED] Ratio={breakout_data['ratio']:.2f}"
        )
        log_breakout_event(video_id, breakout_data["ratio"])
        pattern_memory.boost_recent_pattern(video_id)
        logging.info("[ACTION] Boosting cluster + follow-up priority.")

        # 🔥 NEW – Sequel acceleration (additive only)
        if sequel_chain_id:
            logging.info(f"[SEQUEL ACCELERATION] Chain={sequel_chain_id}")

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

        # 🔥 NEW – Addiction reinforcement bias (additive only)
        if addiction_score > 0.75:
            logging.info("[HIGH ADDICTION SCORE] Reinforcing similar patterns.")

    if saturated_emotion:
        logging.warning(
            f"[EMOTION GOVERNANCE] Penalizing saturated: {saturated_emotion}"
        )
        pattern_memory.penalize_emotion(saturated_emotion)

    if breakout_data["ratio"] < 0.8:
        logging.info("[UNDERPERFORMING] Penalizing structural pattern.")
        pattern_memory.penalize_recent_pattern(video_id)

    logging.info("========== ADAPTIVE OPTIMIZATION COMPLETE ==========")
