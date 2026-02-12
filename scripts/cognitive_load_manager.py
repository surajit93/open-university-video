def segment_script(script, words_per_segment=130):
    words = script.split()
    segments = []
    for i in range(0, len(words), words_per_segment):
        segments.append(" ".join(words[i:i+words_per_segment]))
    return segments

def detect_new_concepts(segment):
    # crude proxy: count capitalized words mid-sentence
    words = segment.split()
    concept_count = sum(1 for w in words if w.istitle())
    return concept_count

def enforce_cognitive_load(script):
    segments = segment_script(script)
    for i, segment in enumerate(segments):
        concepts = detect_new_concepts(segment)
        if concepts > 5:
            raise Exception(f"Cognitive overload detected in segment {i}.")
    return True
