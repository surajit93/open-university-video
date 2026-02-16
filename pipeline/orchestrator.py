# pipeline/orchestrator.py

import time
import logging
import os

from scripts.upload_cadence_enforcer import enforce_upload_cadence
from scripts.runway_guard import enforce_runway_guard
from scripts.performance_tracker import track_performance
from scripts.adaptive_optimizer import run_adaptive_optimization
from scripts.expected_value_model import run_expected_value_projection
from scripts.manual_override import check_manual_override
from scripts.thumbnail_variation_generator import ThumbnailVariationGenerator
from scripts.channel_emotional_index import ChannelEmotionalIndex
from config.channel_growth_plan import load_growth_plan


# ===============================
# FAIL FAST DECORATOR
# ===============================

def fail_fast(stage_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logging.info(f"Stage started: {stage_name}")
                start = time.time()

                result = func(*args, **kwargs)

                duration = time.time() - start
                logging.info(
                    f"Stage completed: {stage_name} | Duration: {duration:.2f}s"
                )
                return result

            except Exception as e:
                logging.error(
                    f"Pipeline halted at stage '{stage_name}': {str(e)}"
                )
                raise RuntimeError(
                    f"Pipeline halted at stage '{stage_name}': {str(e)}"
                )
        return wrapper
    return decorator


# ===============================
# LOGGING SETUP
# ===============================

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ===============================
# WRAPPED CRITICAL STAGES
# ===============================

@fail_fast("manual_override_check")
def run_manual_override_check():
    if check_manual_override():
        logging.warning("Manual override active. Halting pipeline.")
        raise Exception("Manual override active.")


@fail_fast("runway_guard")
def run_runway_guard():
    enforce_runway_guard()


@fail_fast("upload_cadence_enforcement")
def run_upload_cadence():
    enforce_upload_cadence()


@fail_fast("thumbnail_generation")
def run_thumbnail_generation(title_variants):
    if not title_variants:
        raise Exception("No title variants provided.")

    generator = ThumbnailVariationGenerator()
    ranked = generator.generate_and_rank(title_variants)

    if not ranked:
        raise Exception("Thumbnail generation failed.")

    best = ranked[0]

    if not os.path.exists(best["image_path"]):
        raise Exception("Winning thumbnail not created.")

    logging.info(f"Winning thumbnail: {best['image_path']}")
    return best


@fail_fast("performance_tracking")
def run_performance_tracking(video_id):
    track_performance(video_id)


@fail_fast("expected_value_projection")
def run_expected_projection():
    run_expected_value_projection()


@fail_fast("adaptive_optimization")
def run_adaptive(video_id):
    run_adaptive_optimization(video_id)


@fail_fast("emotional_balance_check")
def run_emotional_balance(video_id, emotion_tag):
    index = ChannelEmotionalIndex()

    # Log this video's emotion
    index.log_emotion(video_id, emotion_tag)

    distribution = index.calculate_index()
    logging.info(f"Current emotional distribution: {distribution}")

    needs_balance, message = index.needs_balance()

    if needs_balance:
        logging.warning(message)


# ===============================
# STATE MACHINE
# ===============================

class PipelineOrchestrator:

    def __init__(self, video_id, title_variants=None, emotion_tag="curiosity"):
        self.video_id = video_id
        self.title_variants = title_variants or []
        self.emotion_tag = emotion_tag
        self.growth_plan = load_growth_plan()

    def run(self):
        overall_start = time.time()

        try:
            logging.info("========== PIPELINE STARTED ==========")

            run_manual_override_check()
            run_runway_guard()
            run_upload_cadence()

            best_thumbnail = run_thumbnail_generation(self.title_variants)

            logging.info(
                f"Thumbnail ready: {best_thumbnail['image_path']}"
            )

            logging.info("Upload assumed complete.")

            run_performance_tracking(self.video_id)

            # 🔥 NEW — Emotional mix tracking
            run_emotional_balance(self.video_id, self.emotion_tag)

            run_expected_projection()
            run_adaptive(self.video_id)

            total_duration = time.time() - overall_start
            logging.info(
                f"========== PIPELINE COMPLETED "
                f"in {total_duration:.2f}s =========="
            )

        except Exception as e:
            logging.error(f"PIPELINE FAILED: {str(e)}")
            raise


# ===============================
# ENTRY POINT
# ===============================

if __name__ == "__main__":

    sample_titles = [
        "AI Will Replace You",
        "The AI Collapse Nobody Sees",
        "Why AI Changes Everything",
        "The Secret War Inside AI",
        "Future Shock Is Coming"
    ]

    orchestrator = PipelineOrchestrator(
        video_id="latest_video",
        title_variants=sample_titles,
        emotion_tag="fear"
    )

    orchestrator.run()
