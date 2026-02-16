# scripts/script_generator.py
from scripts.first30_validator import validate_first30
from scripts.policy_guard import PolicyGuard

try:
    from scripts.global_sensitivity_guard import GlobalSensitivityGuard
except Exception:
    GlobalSensitivityGuard = None

try:
    from scripts.callback_injector import inject_callbacks
except Exception:
    def inject_callbacks(script, topic=None):
        return script

try:
    from scripts.series_memory import SeriesMemory
except Exception:
    SeriesMemory = None

try:
    from scripts.narrative_domination_engine import NarrativeDominationEngine
except Exception:
    NarrativeDominationEngine = None

try:
    from scripts.emotion_curve_controller import EmotionCurveController
except Exception:
    EmotionCurveController = None

# 🔥 NEW – Retention Dominance Engine
try:
    from scripts.retention_dominance_engine import RetentionDominanceEngine
except Exception:
    RetentionDominanceEngine = None


class ScriptGenerator:

    def __init__(self):
        self.policy_guard = PolicyGuard()
        self.sensitivity_guard = GlobalSensitivityGuard() if GlobalSensitivityGuard else None
        self.series_memory = SeriesMemory() if SeriesMemory else None

        self.narrative_engine = NarrativeDominationEngine() if NarrativeDominationEngine else None
        self.emotion_engine = EmotionCurveController() if EmotionCurveController else None
        self.retention_engine = RetentionDominanceEngine() if RetentionDominanceEngine else None

    def extract_first30(self, full_script: str) -> str:
        words = full_script.split()
        first30_words = words[:75]
        return " ".join(first30_words)

    def _philosophy_gate(self, script: str):
        required_phrases = ["why this matters", "how it affects you"]
        lower = script.lower()

        for phrase in required_phrases:
            if phrase not in lower:
                raise Exception(f"Philosophy gate failed: '{phrase}' missing.")

        if script.count("you") < 3:
            raise Exception("Philosophy gate failed: insufficient audience framing.")

    def _inject_series_callback(self, script: str, topic: dict):
        if not self.series_memory:
            return script

        series_name = topic.get("series_name")
        if not series_name:
            return script

        previous_hook = self.series_memory.previous_hook(series_name)

        if previous_hook:
            callback_block = (
                f"\n\nEarlier in this series, we explored: {previous_hook}. "
                "Now we take it further.\n"
            )

            if callback_block.strip() not in script:
                script += callback_block

        return script

    def generate(self, topic: dict) -> str:

        script = self._generate_script_logic(topic)

        script = inject_callbacks(script, topic)
        script = self._inject_series_callback(script, topic)

        if self.narrative_engine:
            script = self.narrative_engine.enforce_structure(script)
            script = self.narrative_engine.inject_tension_spikes(script)

        if self.emotion_engine:
            script = self.emotion_engine.analyze(script)
            script = self.emotion_engine.inject_spikes(script)

        # 🔥 Retention Dominance amplification
        if self.retention_engine:
            script = self.retention_engine.amplify_script(script)
            script = self.retention_engine.rewrite_until_personal(script)

        self.policy_guard.check(script)

        if self.sensitivity_guard:
            script = self.sensitivity_guard.sanitize(script)

        first30 = self.extract_first30(script)
        validate_first30(first30)

        self._philosophy_gate(script)

        return script

    def _generate_script_logic(self, topic: dict) -> str:
        return f"{topic['title']} ... generated content ..."
