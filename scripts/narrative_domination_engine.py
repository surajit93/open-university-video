#scripts/narrative_domination_engine.py
import re


class NarrativeDominationEngine:
    """
    Forces escalation ladder + midpoint twist + consequence amplification.
    """

    def enforce_structure(self, script: str) -> str:

        segments = script.split("\n")
        if len(segments) < 4:
            raise Exception("Narrative too short for escalation structure.")

        # Escalation ladder check
        escalation_markers = ["but", "however", "worse", "then", "until"]
        if not any(marker in script.lower() for marker in escalation_markers):
            raise Exception("No escalation ladder detected.")

        # Midpoint twist check (approx middle)
        mid_index = len(script) // 2
        midpoint_section = script[mid_index: mid_index + 300].lower()

        twist_markers = ["but here's the twist", "unexpectedly", "what nobody realized"]
        if not any(t in midpoint_section for t in twist_markers):
            raise Exception("Midpoint twist missing.")

        # Consequence amplification
        consequence_terms = ["this means", "the result", "the consequence", "what happens next"]
        if not any(c in script.lower() for c in consequence_terms):
            raise Exception("Consequence amplification missing.")

        return script

    def inject_tension_spikes(self, script: str, interval=400):
        words = script.split()
        for i in range(interval, len(words), interval):
            words.insert(i, "But it gets worse.")
        return " ".join(words)
