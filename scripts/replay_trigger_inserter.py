# scripts/replay_trigger_inserter.py

from typing import List


class ReplayTriggerInserter:

    def __init__(self):
        self.triggers = [
            "But here’s what most people miss.",
            "Now this changes everything.",
            "The real shift hasn’t even started yet.",
            "And this is where it gets uncomfortable."
        ]

    def insert(self, paragraphs: List[str]) -> List[str]:
        if len(paragraphs) < 4:
            return paragraphs

        insert_index = int(len(paragraphs) * 0.75)

        trigger = self.triggers[insert_index % len(self.triggers)]

        paragraphs.insert(insert_index, trigger)

        return paragraphs
