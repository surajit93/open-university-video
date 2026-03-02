"""
light_leak_overlay.py
Adds cinematic light overlay.
"""

from moviepy.editor import VideoFileClip, CompositeVideoClip


class LightLeakOverlay:

    def apply(self, base_clip, overlay_path="assets/overlays/light_leak.mp4"):

        overlay = VideoFileClip(overlay_path).set_opacity(0.3)
        overlay = overlay.set_duration(base_clip.duration)

        return CompositeVideoClip([base_clip, overlay])
