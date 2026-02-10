# scripts/validate_output.py

import json
import sys
from pathlib import Path
from collections import OrderedDict

# ================================
# CONFIG
# ================================

SLIDE_PLAN_FILE = Path("slide_plan.json")
AUDIO_MAP_FILE = Path("slide_audio_map.json")

ALLOWED_VISUALS = {
    "CONCEPT_DIAGRAM",
    "FLOW_DIAGRAM",
    "SYSTEM_DIAGRAM",
    "CODE_BLOCK",
    "MATH_FORMULA",
    "PHOTO_REFERENCE",
    "TEXT_ONLY",
}

# ================================
# AUTO-REPAIR (DIAGRAMS)
# ================================

def repair_diagram_boxes(slides: list) -> bool:
    repaired = False

    for slide in slides:
        vs = slide.get("visual_strategy")
        left = slide.get("left_panel_plan") or {}

        if vs in {"CONCEPT_DIAGRAM", "FLOW_DIAGRAM", "SYSTEM_DIAGRAM"}:
            boxes = left.get("diagram_boxes")

            if not boxes or not isinstance(boxes, list):
                core = (
                    slide.get("teaching_intent", {})
                    .get("core_idea", "Core Concept")
                )

                left["diagram_boxes"] = [
                    {"id": "A", "label": core},
                    {"id": "B", "label": "Key Mechanism"},
                    {"id": "C", "label": "Outcome / Effect"},
                ]

                left.setdefault(
                    "diagram_relationships",
                    "A leads to B, which produces C"
                )

                slide["left_panel_plan"] = left
                repaired = True

    return repaired

# ================================
# AUTO-REPAIR (AUDIO ALIGNMENT)
# ================================

def repair_audio_alignment(audio_map: list) -> list:
    merged = OrderedDict()

    for item in audio_map:
        sid = item.get("slide_id")
        text = item.get("spoken_text", "").strip()

        if sid not in merged:
            merged[sid] = {
                "slide_id": sid,
                "spoken_text": text
            }
        else:
            if text:
                merged[sid]["spoken_text"] += "\n\n" + text

    return list(merged.values())

# ================================
# AUTO-REPAIR (RIGHT PANEL GIST)
# ================================

def repair_missing_gist(slides: list) -> bool:
    repaired = False

    for slide in slides:
        gist = slide.get("right_panel_gist")
        if not gist or not gist.strip():
            intent = slide.get("teaching_intent", {})
            slide["right_panel_gist"] = (
                intent.get("core_idea")
                or intent.get("learning_goal")
                or "Key takeaway of this slide"
            )
            repaired = True

    return repaired

# ================================
# VALIDATION LOGIC
# ================================

def validate(slide_plan: dict, audio_map: list):
    if "slides" not in slide_plan:
        raise AssertionError("slide_plan.json missing top-level 'slides' key")

    slides = slide_plan["slides"]

    if not slides:
        raise AssertionError("slide_plan.json contains zero slides")

    if not isinstance(audio_map, list):
        raise AssertionError("slide_audio_map.json must be a list")

    # ----------------------------
    # 🔧 AUTO-REPAIR: DIAGRAMS
    # ----------------------------
    if repair_diagram_boxes(slides):
        SLIDE_PLAN_FILE.write_text(
            json.dumps(slide_plan, indent=2),
            encoding="utf-8"
        )
        print("🛠️  slide_plan.json auto-repaired (diagram_boxes added)")

    # ----------------------------
    # 🔧 AUTO-REPAIR: GIST
    # ----------------------------
    if repair_missing_gist(slides):
        SLIDE_PLAN_FILE.write_text(
            json.dumps(slide_plan, indent=2),
            encoding="utf-8"
        )
        print("🛠️  slide_plan.json auto-repaired (right_panel_gist added)")

    # ----------------------------
    # 🔧 AUTO-REPAIR: AUDIO
    # ----------------------------
    original_audio_len = len(audio_map)
    audio_map = repair_audio_alignment(audio_map)

    if len(audio_map) != original_audio_len:
        AUDIO_MAP_FILE.write_text(
            json.dumps(audio_map, indent=2),
            encoding="utf-8"
        )
        print("🛠️  slide_audio_map.json auto-repaired (merged duplicate slide_id entries)")

    # ----------------------------
    # slide_id integrity
    # ----------------------------
    slide_ids = [s.get("slide_id") for s in slides]
    expected_ids = list(range(1, len(slide_ids) + 1))

    if slide_ids != expected_ids:
        raise AssertionError(
            f"slide_id must be contiguous starting at 1.\n"
            f"Expected: {expected_ids}\n"
            f"Found:    {slide_ids}"
        )

    # ----------------------------
    # audio alignment
    # ----------------------------
    audio_ids = [a.get("slide_id") for a in audio_map]

    if audio_ids != slide_ids:
        raise AssertionError(
            "slide_plan.json and slide_audio_map.json are misaligned.\n"
            f"Slides: {slide_ids}\n"
            f"Audio:  {audio_ids}"
        )

    # ----------------------------
    # per-slide validation
    # ----------------------------
    for slide in slides:
        sid = slide["slide_id"]

        vs = slide.get("visual_strategy")
        if not vs:
            raise AssertionError(f"Slide {sid}: missing visual_strategy")

        if vs not in ALLOWED_VISUALS:
            raise AssertionError(
                f"Slide {sid}: invalid visual_strategy '{vs}'"
            )

        left = slide.get("left_panel_plan")
        if left is None:
            raise AssertionError(f"Slide {sid}: missing left_panel_plan")

        if vs in {"CONCEPT_DIAGRAM", "FLOW_DIAGRAM", "SYSTEM_DIAGRAM"}:
            if not isinstance(left.get("diagram_boxes"), list):
                raise AssertionError(
                    f"Slide {sid}: '{vs}' requires diagram_boxes"
                )

        if vs == "PHOTO_REFERENCE" and not left.get("photo_query"):
            raise AssertionError(
                f"Slide {sid}: PHOTO_REFERENCE requires photo_query"
            )

        if vs == "CODE_BLOCK" and not left.get("description"):
            raise AssertionError(
                f"Slide {sid}: CODE_BLOCK requires description"
            )

        if vs == "MATH_FORMULA" and not left.get("math_formula"):
            raise AssertionError(
                f"Slide {sid}: MATH_FORMULA requires math_formula"
            )

        gist = slide.get("right_panel_gist")
        if not gist or not gist.strip():
            raise AssertionError(
                f"Slide {sid}: right_panel_gist missing or empty"
            )

    # ----------------------------
    # audio text validation
    # ----------------------------
    for item in audio_map:
        sid = item.get("slide_id")
        text = item.get("spoken_text")

        if not sid:
            raise AssertionError("audio_map entry missing slide_id")

        if not text or not text.strip():
            raise AssertionError(
                f"spoken_text missing or empty for slide {sid}"
            )

    print("✔ slide_plan.json and slide_audio_map.json validation passed")

# ================================
# ENTRY POINT
# ================================

def main():
    if not SLIDE_PLAN_FILE.exists():
        print("ERROR: slide_plan.json not found")
        sys.exit(1)

    if not AUDIO_MAP_FILE.exists():
        print("ERROR: slide_audio_map.json not found")
        sys.exit(1)

    slide_plan = json.loads(SLIDE_PLAN_FILE.read_text(encoding="utf-8"))
    audio_map = json.loads(AUDIO_MAP_FILE.read_text(encoding="utf-8"))

    validate(slide_plan, audio_map)

if __name__ == "__main__":
    main()
