"""
render_orchestrator.py
Enterprise render control with memory discipline.
"""

from pathlib import Path
from video_core.timeline_builder import TimelineBuilder


class RenderOrchestrator:

    def __init__(self, output_dir="renders"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timeline_builder = TimelineBuilder()

    def render(self, scenes, filename="final_output.mp4"):

        final_video = self.timeline_builder.build(scenes)

        output_path = self.output_dir / filename

        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=8,
            preset="medium",
            bitrate="8000k"
        )

        final_video.close()

        return output_path
