def compute_scene_intensity(scene_text):
    intensity_words = ["collapse", "crisis", "power", "control", "risk", "unpredictable"]
    return sum(1 for w in intensity_words if w in scene_text.lower())

def validate_tension_curve(scenes):
    intensities = [compute_scene_intensity(s) for s in scenes]

    if len(intensities) < 3:
        return True

    if max(intensities) <= intensities[0]:
        raise Exception("Tension curve invalid: no escalation beyond hook.")

    if intensities[-1] < intensities[len(intensities)//2]:
        raise Exception("Tension curve drops before ending.")

    return True
