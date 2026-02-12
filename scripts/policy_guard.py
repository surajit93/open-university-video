# scripts/policy_guard.py

import re


class PolicyGuard:

    def __init__(self):
        self.risky_patterns = [
            r"\bworld war\b",
            r"\bglobal collapse imminent\b",
            r"\bgovernment conspiracy\b",
            r"\bsecret plan\b"
        ]

    def check(self, script: str):
        for pattern in self.risky_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                raise ValueError(
                    f"Policy risk detected: '{pattern}' found."
                )

        return True
