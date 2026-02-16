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


class ScriptGenerator:

    def __init__(self):
        self.policy_guard = PolicyGuard()
        self.sensitivity_guard = GlobalSensitivityGuard() if GlobalSensitivityGuard else None

    def extract_first30(self, full_script: str) -> str:
        """
        Roughly approximate first 30 seconds.
        Assumes ~150 words per minute narration.
        30 sec ≈ 75 words.
        """
        words = full_script.split()
        first30_words = words[:75]
        return " ".join(first30_words)

    # 🔥 NEW: Philosophy hard gate
    def _philosophy_gate(self, script: str):
        required_phrases = ["why this matters", "how it affects you"]
        lower = script.lower()
        for phrase in required_phrases:
            if phrase not in lower:
                raise Exception(f"Philosophy gate failed: '{phrase}' missing.")

    def generate(self, topic: dict) -> str:
        """
        Main generation entry point.
        """

        # --- your existing generation logic ---
        script = self._generate_script_logic(topic)

        # 🔥 NEW: Callback injection
        script = inject_callbacks(script, topic)

        # 🔥 1️⃣ POLICY + SENSITIVITY CHECK
        self.policy_guard.check(script)

        # 🔥 NEW: Sensitivity hard enforcement
        if self.sensitivity_guard:
            script = self.sensitivity_guard.sanitize(script)

        # 🔥 2️⃣ FIRST 30 VALIDATION
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
