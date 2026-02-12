# scripts/competitor_analyzer.py

from typing import List, Dict
import statistics


class CompetitorAnalyzer:

    def analyze(self, competitor_videos: List[Dict]) -> Dict:
        """
        competitor_videos example:
        [
            {
                "duration": 480,
                "title_length": 62,
                "thumbnail_word_count": 4,
                "views_per_day": 32000
            }
        ]
        """

        durations = [v["duration"] for v in competitor_videos]
        title_lengths = [v["title_length"] for v in competitor_videos]
        thumb_words = [v["thumbnail_word_count"] for v in competitor_videos]
        velocity = [v["views_per_day"] for v in competitor_videos]

        return {
            "avg_duration": statistics.mean(durations) if durations else 0,
            "avg_title_length": statistics.mean(title_lengths) if title_lengths else 0,
            "avg_thumbnail_words": statistics.mean(thumb_words) if thumb_words else 0,
            "avg_views_per_day": statistics.mean(velocity) if velocity else 0,
            "competition_intensity": statistics.mean(velocity) if velocity else 0
        }
