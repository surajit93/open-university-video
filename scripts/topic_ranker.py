# scripts/topic_ranker.py

from typing import Dict


class TopicRanker:

    def score_topic(self, topic: Dict) -> Dict:
        """
        topic example:
        {
            "title": "...",
            "search_demand": 0.7,
            "emotional_intensity": 0.8,
            "controversy": 0.5,
            "evergreen": 0.6,
            "cluster_fit": 0.9
        }
        """

        weights = {
            "search_demand": 0.25,
            "emotional_intensity": 0.20,
            "controversy": 0.15,
            "evergreen": 0.20,
            "cluster_fit": 0.20
        }

        score = 0
        for key, weight in weights.items():
            score += topic.get(key, 0) * weight

        return {
            "title": topic["title"],
            "priority_score": round(score, 3)
        }

    def rank(self, topics: list) -> list:
        scored = [self.score_topic(t) for t in topics]
        return sorted(scored, key=lambda x: x["priority_score"], reverse=True)
