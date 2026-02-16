# scripts/philosophy_validator.py

REQUIRED_CONCEPTS = [
    "why this matters",
    "this affects you",
    "what changes",
    "what this means for you"
]


def enforce_philosophy(script_text):
    script_lower = script_text.lower()

    matches = 0
    for phrase in REQUIRED_CONCEPTS:
        if phrase in script_lower:
            matches += 1

    if matches < 1:
        raise RuntimeError(
            "Philosophy enforcement failed. Script lacks viewer impact framing."
        )

    return True
