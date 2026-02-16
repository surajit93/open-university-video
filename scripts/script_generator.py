# scripts/script_generator.py
from scripts.first30_validator import validate_first30
from scripts.policy_guard import PolicyGuard

# 🔥 NEW
try:
    from scripts.global_sensitivity_guard import GlobalSensitivityGuard
except Exception:
    GlobalSensitivityGuard = None

try:
    from scripts.callback_injector import inject_callbacks
except Exception:
    def inject_callbacks(script, topic=None):
        return script

# 🔥 NEW – Series memory integration (additive only)
try:
    from scripts.series_memory import SeriesMemory
except Exception:
    SeriesMemory = None


class ScriptGenerator:

    def __init__(self):
        self.policy_guard = PolicyGuard()
        self.sensitivity_guard = GlobalSensitivityGuard() if GlobalSensitivityGuard else None
        self.series_memory = SeriesMemory() if SeriesMemory else None

    def extract_first30(self, full_script: str) -> str:
        """
        Roughly approximate first 30 seconds.
        Assumes ~150 words per minute narration.
        30 sec ≈ 75 words.
        """
        words = full_script.split()
        first30_words = words[:75]
        return " ".join(first30_words)

    # 🔥 NEW: Philosophy hard gate (strengthened but additive only)
    def _philosophy_gate(self, script: str):
        required_phrases = ["why this matters", "how it affects you"]
        lower = script.lower()

        for phrase in required_phrases:
            if phrase not in lower:
                raise Exception(f"Philosophy gate failed: '{phrase}' missing.")

        # 🔥 Additional structural enforcement (additive only)
        if script.count("you") < 3:
            raise Exception("Philosophy gate failed: insufficient audience framing.")

    # 🔥 NEW: Series callback enforcement (additive only)
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
        """
        Main generation entry point.
        """

        # --- your existing generation logic ---
        script = self._generate_script_logic(topic)

        # 🔥 NEW: Callback injection (existing hook preserved)
        script = inject_callbacks(script, topic)

        # 🔥 NEW: Guaranteed series-level callback injection
        script = self._inject_series_callback(script, topic)

        # 🔥 1️⃣ POLICY CHECK (unchanged)
        self.policy_guard.check(script)

        # 🔥 NEW: Sensitivity hard enforcement (existing behavior preserved)
        if self.sensitivity_guard:
            script = self.sensitivity_guard.sanitize(script)

        # 🔥 2️⃣ FIRST 30 VALIDATION (unchanged)
        first30 = self.extract_first30(script)
        validate_first30(first30)

        # 🔥 NEW: Philosophy gate enforcement
        self._philosophy_gate(script)

        return script

    def _generate_script_logic(self, topic: dict) -> str:
        """
        Your existing generation logic stays here.
        """
        return f"{topic['title']} ... generated content ..."
