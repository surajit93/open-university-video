# scripts/cluster_profit_optimizer.py

class ClusterProfitOptimizer:

    def rank_clusters(self, cluster_metrics: list):
        """
        cluster_metrics format:
        [
            {"cluster": "AI", "avg_views": 120000, "avg_rpm": 6.5},
            ...
        ]
        """

        for cluster in cluster_metrics:
            cluster["expected_revenue"] = (
                cluster["avg_views"] / 1000.0
            ) * cluster["avg_rpm"]

        return sorted(
            cluster_metrics,
            key=lambda x: x["expected_revenue"],
            reverse=True
        )
