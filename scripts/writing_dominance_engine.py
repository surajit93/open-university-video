# scripts/writing_dominance_engine.py

import re
from statistics import mean


class WritingDominanceEngine:
    """
    Unified Writing Intelligence Engine

    Includes:
    - Psychological master prompt builder
    - Multi-pass rewrite loop
    - Storycraft evaluation
    - Tension density measurement
    """

    # ============================================================
    # SYSTEM DIRECTIVE
    # ============================================================

    SYSTEM_DIRECTIVE = """
You are an elite psychological storyteller.

You do NOT write informational content.
You write escalating psychological tension.

Rules:
- Speak directly using "you".
- Create identity pressure.
- Imply personal consequence.
- Escalate stakes every 30–40 seconds.
- Add inevitability.
- Midpoint twist is mandatory.
- Remove fluff.
- End with amplified consequence.
"""

    ESCALATION_STRUCTURE = """
Structure:
1. Immediate personal hook
2. Escalate consequences
3. Midpoint twist
4. Amplify outcome
5. Personal future implication
"""

    # ============================================================
    # TENSION MODELS
    # ============================================================

    TENSION_WORDS = [
        "risk", "threat", "collapse", "danger",
        "before", "now", "replace", "loss",
        "survival", "crisis", "fail", "warning",
        "exposed", "decline", "vulnerable"
    ]

    BLOCK_SIZE = 120

    # ============================================================
    # INIT
    # ============================================================

    def __init__(self, llm_callable):
        """
        llm_callable(prompt:str) -> str
        """
        self.llm = llm_callable

    # ============================================================
    # MASTER PROMPT
    # ============================================================

    def build_prompt(self, topic_title: str) -> str:
        return f"""
{self.SYSTEM_DIRECTIVE}

Topic: {topic_title}

{self.ESCALATION_STRUCTURE}

Write the full script now.
"""

    # ============================================================
    # REWRITE LOOP
    # ============================================================

    def _rewrite_prompt(self, script: str, pass_number: int) -> str:
        return f"""
Rewrite Pass {pass_number}.

Increase:
- Psychological pressure
- Second-person intensity
- Consequence clarity
- Escalation velocity

Remove:
- Filler
- Neutral explanation
- Generic tone

Script:
{script}
"""

    def rewrite(self, script: str, passes: int = 3) -> str:
        current = script
        for i in range(1, passes + 1):
            prompt = self._rewrite_prompt(current, i)
            current = self.llm(prompt)
        return current

    # ============================================================
    # STORYCRAFT EVALUATION
    # ============================================================

    def tension_density(self, script: str) -> float:
        words = script.lower().split()
        if not words:
            return 0.0

        count = sum(1 for w in words if any(t in w for t in self.TENSION_WORDS))
        return count / len(words)

    def second_person_ratio(self, script: str) -> float:
        words = script.lower().split()
        if not words:
            return 0.0

        count = words.count("you") + words.count("your")
        return count / len(words)

    def escalation_continuity(self, script: str) -> float:
        sentences = re.split(r"[.!?]", script)
        lengths = [len(s.split()) for s in sentences if s.strip()]

        if len(lengths) < 3:
            return 0.0

        increases = sum(
            1 for i in range(1, len(lengths))
            if lengths[i] >= lengths[i - 1]
        )

        return increases / len(lengths)

    def evaluate(self, script: str) -> dict:
        td = self.tension_density(script)
        sp = self.second_person_ratio(script)
        ec = self.escalation_continuity(script)

        approved = (
            td > 0.01 and
            sp > 0.015 and
            ec > 0.4
        )

        return {
            "tension_density": round(td, 4),
            "second_person_ratio": round(sp, 4),
            "escalation_score": round(ec, 3),
            "approved": approved
        }

    # ============================================================
    # BLOCK TENSION ANALYSIS
    # ============================================================

    def _blockify(self, script: str):
        words = script.split()
        return [
            words[i:i+self.BLOCK_SIZE]
            for i in range(0, len(words), self.BLOCK_SIZE)
        ]

    def block_tension_analysis(self, script: str) -> dict:
        blocks = self._blockify(script)
        scores = []

        for block in blocks:
            if not block:
                scores.append(0)
                continue

            count = sum(
                1 for w in block
                if any(t in w.lower() for t in self.TENSION_WORDS)
            )
            scores.append(count / len(block))

        flat_blocks = [
            i for i, s in enumerate(scores)
            if s < 0.005
        ]

        return {
            "block_scores": scores,
            "flat_blocks": flat_blocks,
            "avg_tension": round(mean(scores), 4) if scores else 0
        }

    # ============================================================
    # FULL PIPELINE
    # ============================================================

    def generate_high_retention_script(self, topic_title: str, passes: int = 3):
        # 1️⃣ Build psychological prompt
        prompt = self.build_prompt(topic_title)

        # 2️⃣ Initial generation
        script = self.llm(prompt)

        # 3️⃣ Rewrite tightening loop
        script = self.rewrite(script, passes=passes)

        # 4️⃣ Evaluate quality
        evaluation = self.evaluate(script)

        # 5️⃣ Block-level tension analysis
        block_analysis = self.block_tension_analysis(script)

        return {
            "script": script,
            "evaluation": evaluation,
            "block_analysis": block_analysis
        }
