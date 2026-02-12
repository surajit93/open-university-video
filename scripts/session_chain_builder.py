# scripts/session_chain_builder.py

from typing import List, Dict


class SessionChainBuilder:

    def build_chain(self, current_video: Dict, cluster_videos: List[Dict]) -> Dict:
        """
        current_video:
        {
            "video_id": "...",
            "cluster": "ai_future"
        }

        cluster_videos:
        [
            {"video_id": "...", "retention_score": 0.62},
            {"video_id": "...", "retention_score": 0.71}
        ]
        """

        sorted_candidates = sorted(
            cluster_videos,
            key=lambda x: x.get("retention_score", 0),
            reverse=True
        )

        next_recommendations = sorted_candidates[:2]

        return {
            "end_screen_targets": [v["video_id"] for v in next_recommendations],
            "description_links": [v["video_id"] for v in next_recommendations]
        }
