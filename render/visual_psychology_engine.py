# render/visual_psychology_engine.py

import math
import hashlib


class VisualPsychologyEngine:
    """
    SUPER DUPER Visual Retention Engine

    Purpose:
    Engineer dopamine cycles, contrast rhythm, motion shocks,
    anti-template enforcement, and audio-tension sync.

    This is NOT cosmetic.
    This is retention engineering.
    """

    # ============================================================
    # INIT CONFIG
    # ============================================================

    def __init__(
        self,
        contrast_cycle_length=4,
        spike_interval_seconds=40,
        max_audio_gain=1.4,
        sound_spike_threshold=0.75
    ):
        self.contrast_cycle_length = contrast_cycle_length
        self.spike_interval_seconds = spike_interval_seconds
        self.max_audio_gain = max_audio_gain
        self.sound_spike_threshold = sound_spike_threshold
        self._previous_signatures = set()

    # ============================================================
    # SCENE SIGNATURE (ANTI-TEMPLATE CONTROL)
    # ============================================================

    def _signature(self, scene: dict) -> str:
        layout_keys = (
            scene.get("background"),
            scene.get("headline"),
            scene.get("accent_element"),
            scene.get("foreground_text"),
        )
        return hashlib.md5(str(layout_keys).encode()).hexdigest()

    # ============================================================
    # FULL PIPELINE
    # ============================================================

    def apply(self, scenes: list, tension_scores: list = None) -> list:
        """
        Applies complete visual psychology pipeline.

        Order:
        1. Anti-template enforcement
        2. Contrast rhythm cycling
        3. Motion spike scheduling
        4. Audio intensity sync
        5. Cinematic sound injection
        """

        if tension_scores is None:
            tension_scores = [0.5] * len(scenes)

        enhanced = []
        elapsed_time = 0

        for i, scene in enumerate(scenes):

            # ====================================================
            # 1️⃣ ANTI-TEMPLATE ENFORCEMENT
            # ====================================================

            sig = self._signature(scene)

            if sig in self._previous_signatures:
                scene["variation_injected"] = True
                scene["accent_element"] = "dynamic_pulse"
                scene["background_variant"] = "alt_tone"
                scene["layout_shift"] = True
            else:
                scene["variation_injected"] = False
                scene["layout_shift"] = False

            self._previous_signatures.add(sig)

            # ====================================================
            # 2️⃣ CONTRAST RHYTHM CYCLE
            # ====================================================

            phase = i % self.contrast_cycle_length

            brightness = 0.8 + (
                0.4 * math.sin((phase / self.contrast_cycle_length) * math.pi)
            )

            motion_density = 1 + (phase * 0.25)
            scale_intensity = 1 + (0.07 * phase)

            scene["visual_contrast"] = {
                "brightness_multiplier": round(brightness, 3),
                "motion_density": round(motion_density, 3),
                "scale_intensity": round(scale_intensity, 3),
                "contrast_phase": phase
            }

            # ====================================================
            # 3️⃣ MOTION SPIKE SCHEDULER
            # ====================================================

            duration = scene.get("duration", 8)

            if elapsed_time >= self.spike_interval_seconds:
                scene["motion_spike"] = {
                    "zoom": 1.18,
                    "shake": 0.45,
                    "impact_transition": True,
                    "velocity_boost": 1.2
                }
                elapsed_time = 0
            else:
                scene["motion_spike"] = None

            elapsed_time += duration

            # ====================================================
            # 4️⃣ AUDIO INTENSITY MAPPING
            # ====================================================

            tension = (
                tension_scores[i]
                if i < len(tension_scores)
                else 0.5
            )

            gain = 1 + (tension * (self.max_audio_gain - 1))

            scene["audio_intensity"] = {
                "music_gain": round(gain, 3),
                "low_freq_boost": tension > 0.7,
                "percussion_layer": tension > 0.6
            }

            # ====================================================
            # 5️⃣ CINEMATIC SOUND DESIGN
            # ====================================================

            if tension >= self.sound_spike_threshold:
                scene["sound_fx"] = [
                    "impact_hit.wav",
                    "low_sub_pulse.wav",
                    "cinematic_riser.wav"
                ]
            elif tension > 0.55:
                scene["sound_fx"] = ["whoosh_medium.wav"]
            else:
                scene["sound_fx"] = ["whoosh_soft.wav"]

            enhanced.append(scene)

        return enhanced
