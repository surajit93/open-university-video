"""
motion_template_registry.py
Central registry mapping motion names to implementations.
"""

from motion_engine.kenburns import KenBurnsMotion
from motion_engine.parallax import ParallaxMotion
from motion_engine.punch_zoom import PunchZoomMotion
from motion_engine.rotation_drift import RotationDriftMotion
from motion_engine.glitch_hit import GlitchHitMotion
from motion_engine.light_leak_overlay import LightLeakOverlay


class MotionTemplateRegistry:

    def __init__(self):
        self.registry = {
            "kenburns": KenBurnsMotion(),
            "parallax": ParallaxMotion(),
            "punch_zoom": PunchZoomMotion(),
            "rotation_drift": RotationDriftMotion(),
            "glitch_hit": GlitchHitMotion(),
            "light_leak": LightLeakOverlay(),
        }

    def get(self, motion_name: str):
        return self.registry.get(motion_name, self.registry["kenburns"])
