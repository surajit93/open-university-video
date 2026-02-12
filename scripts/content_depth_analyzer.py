import re

VAGUE_WORDS = ["many", "very", "huge", "massive", "some experts", "people say"]

def count_numbers(text):
    return len(re.findall(r"\d+", text))

def vague_penalty(text):
    return sum(1 for word in VAGUE_WORDS if word in text.lower())

def compute_depth_score(script):
    word_count = len(script.split())
    number_count = count_numbers(script)
    vague_count = vague_penalty(script)

    factual_density = number_count / max(word_count, 1)
    score = factual_density * 100 - vague_count

    return round(score, 2)

def reject_if_shallow(script, threshold=1.5):
    score = compute_depth_score(script)
    if score < threshold:
        raise Exception("Script rejected: insufficient depth.")
    return score
