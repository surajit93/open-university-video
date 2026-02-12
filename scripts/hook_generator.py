import random
import re

EMOTIONAL_WORDS = ["collapse", "destroy", "unstoppable", "shocking", "hidden", "dangerous"]
CURIOSITY_PATTERNS = ["what happens when", "no one is talking about", "the truth about", "before it's too late"]

def score_emotional_intensity(text):
    score = sum(1 for word in EMOTIONAL_WORDS if word in text.lower())
    return score

def score_curiosity_gap(text):
    score = sum(1 for pattern in CURIOSITY_PATTERNS if pattern in text.lower())
    return score

def generate_hook_variations(topic):
    templates = [
        f"What happens when {topic} changes everything?",
        f"The hidden truth about {topic} no one is talking about.",
        f"{topic} could destroy more than you think.",
        f"Before it's too late: the real impact of {topic}.",
        f"{topic} is evolving faster than anyone expected."
    ]
    return templates

def select_best_hook(topic):
    hooks = generate_hook_variations(topic)
    scored = []

    for hook in hooks:
        emotional = score_emotional_intensity(hook)
        curiosity = score_curiosity_gap(hook)
        total = emotional * 2 + curiosity * 3
        scored.append((hook, total))

    best = max(scored, key=lambda x: x[1])
    return best[0], scored
