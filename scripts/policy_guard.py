# scripts/policy_guard.py

import re
from scripts.global_sensitivity_guard import GlobalSensitivityGuard


class PolicyGuard:

    def __init__(self):
        self.risky_patterns = [
            r"\bworld war\b",
            r"\bglobal collapse imminent\b",
            r"\bgovernment conspiracy\b",
            r"\bsecret plan\b"
        ]

        # 🔥 NEW — Global sensitivity layer
        self.sensitivity_guard = GlobalSensitivityGuard()

    def check(self, script: str) -> bool:
        """
        Full policy enforcement pipeline:
        1️⃣ Global sensitivity sanitization
        2️⃣ Hard policy risk detection
        """

        # 🔥 STEP 1 — Global sensitivity sanitize
        script = self.sensitivity_guard.sanitize(script)

        # 🔥 STEP 2 — Hard policy violation detection
        for pattern in self.risky_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                raise ValueError(
                    f"Policy risk detected: '{pattern}' found."
                )

        return True
