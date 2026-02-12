# scripts/global_sensitivity_guard.py

import re


class GlobalSensitivityGuard:

    SENSITIVE_PATTERNS = [
        r"\bAmerica will collapse\b",
        r"\bChina is doomed\b",
        r"\bEurope is finished\b",
    ]

    def sanitize(self, script: str) -> str:
        for pattern in self.SENSITIVE_PATTERNS:
            script = re.sub(
                pattern,
                "Some regions may face structural challenges",
                script,
                flags=re.IGNORECASE
            )

        return script
