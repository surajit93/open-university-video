"""
retention_controller.py
Injects pattern interrupts and contrast shifts.
"""

from moviepy.editor import vfx


class RetentionController:

    def enhance(self, clip, scene):

        if scene.retention.pattern_interrupt:
            clip = clip.fx(vfx.colorx, 1.2)

        if scene.retention.contrast_shift:
            clip = clip.fx(vfx.lum_contrast, 10, 30, 128)

        return clip
