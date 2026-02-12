# scripts/trend_shift_detector.py

import sqlite3
from collections import Counter


class TrendShiftDetector:

    def __init__(self, db_path="data/performance.db"):
        self.db_path = db_path

    def cluster_distribution(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT cluster_name FROM performance
        """)
        rows = cursor.fetchall()
        conn.close()

        clusters = [r[0] for r in rows if r[0]]
        return Counter(clusters)

    def detect_shift(self, threshold=0.4):
        distribution = self.cluster_distribution()
        total = sum(distribution.values()) or 1

        cluster_ratios = {
            k: v / total
            for k, v in distribution.items()
        }

        dominant_cluster = max(cluster_ratios, key=cluster_ratios.get) \
            if cluster_ratios else None

        return {
            "distribution": cluster_ratios,
            "dominant_cluster": dominant_cluster,
            "dominance_ratio": cluster_ratios.get(dominant_cluster, 0),
            "needs_rebalance": cluster_ratios.get(dominant_cluster, 0) > threshold
        }
