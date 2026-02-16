# scripts/script_generator.py

from scripts.first30_validator import validate_first30
from scripts.policy_guard import PolicyGuard


class ScriptGenerator:

    def __init__(self):
        self.policy_guard = PolicyGuard()

    def extract_first30(self, full_script: str) -> str:
        """
        Roughly approximate first 30 seconds.
        Assumes ~150 words per minute narration.
        30 sec ≈ 75 words.
        """
        words = full_script.split()
        first30_words = words[:75]
        return " ".join(first30_words)

    def generate(self, topic: dict) -> str:
        """
        Main generation entry point.
        """

        # --- your existing generation logic ---
        script = self._generate_script_logic(topic)

        # 🔥 1️⃣ POLICY + SENSITIVITY CHECK
        self.policy_guard.check(script)

        # 🔥 2️⃣ FIRST 30 VALIDATION
        first30 = self.extract_first30(script)
        validate_first30(first30)

        return script

    def _generate_script_logic(self, topic: dict) -> str:
        """
        Your existing generation logic stays here.
        """
        # Placeholder for your LLM or template logic
        return f"{topic['title']} ... generated content ..."
