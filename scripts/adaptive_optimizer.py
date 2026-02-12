import sqlite3
import json
from scripts.runway_guard import check_runway
from config_loader import load_growth_plan

PERF_DB = "data/performance.db"

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

def run_adaptive_optimization():
    growth_plan = load_growth_plan()
    allow_pivot = check_runway(growth_plan)

    rows = get_last_n(growth_plan["optimization_window"])
    if not rows:
        print("Not enough data for optimization.")
        return

    avg_ctr = sum(r[0] for r in rows) / len(rows)
    avg_retention = sum(r[1] for r in rows) / len(rows)
    avg_velocity = sum(r[2] for r in rows) / len(rows)

    if avg_ctr < 4:
        print("CTR low: Trigger thumbnail regeneration logic.")

    if avg_retention < 40:
        print("Retention low: Penalize hook pattern.")

    if avg_velocity > 20:
        print("Strong momentum: Boost cluster priority.")

    if allow_pivot and avg_velocity < 5:
        print("Velocity flat post-runway: Consider angle shift.")
