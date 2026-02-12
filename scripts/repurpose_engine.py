# scripts/repurpose_engine.py

from typing import Dict, List


class RepurposeEngine:

    def extract_shorts(self, scenes: List[dict]) -> List[dict]:
        """
        Extract high-intensity 30–60s vertical cuts.
        """
        shorts = []

        for scene in scenes:
            if scene.get("intensity", 0) > 0.75:
                shorts.append({
                    "type": "short",
                    "duration_target": 45,
                    "content": scene
                })

        return shorts[:3]  # max 3 shorts per video

    def generate_thread_summary(self, script: str) -> List[str]:
        """
        Generate Twitter/X thread structure.
        """
        lines = script.split(".")
        thread = []

        for idx, line in enumerate(lines[:8]):
            if line.strip():
                thread.append(f"{idx+1}/ {line.strip()}.")

        return thread

    def generate_blog_summary(self, script: str) -> str:
        """
        Long-form summary version.
        """
        return (
            "Summary:\n\n"
            + script[:1500]
            + "\n\nWhat does this mean for you?"
        )
