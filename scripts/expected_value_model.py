import sqlite3
import numpy as np

DB_PATH = "data/performance.db"

def calculate_expected_growth(months=6):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT views FROM video_performance")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No data for projection.")
        return None

    avg_views = np.mean([r[0] for r in rows])
    uploads_per_month = 8

    projected = avg_views * uploads_per_month * months

    print(f"Projected {months}-month views: {int(projected)}")
    return projected
