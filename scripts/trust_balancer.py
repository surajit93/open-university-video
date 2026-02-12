# scripts/trust_balancer.py

import re


class TrustBalancer:

    def __init__(self):
        self.absolute_patterns = [
            r"\bwill destroy\b",
            r"\bwill end\b",
            r"\bguaranteed\b",
            r"\bno doubt\b",
            r"\bdefinitely\b"
        ]

    def normalize(self, script: str) -> str:
        updated = script

        for pattern in self.absolute_patterns:
            updated = re.sub(
                pattern,
                lambda m: m.group(0).replace("will", "could").replace("definitely", "likely"),
                updated,
                flags=re.IGNORECASE
            )

        return updated
