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
                logging.info(f"[START] {stage_name}")
                start = time.time()

                result = func(*args, **kwargs)

                duration = time.time() - start
                logging.info(
                    f"[END] {stage_name} | Duration: {duration:.2f}s"
                )
                return result

            except Exception as e:
                logging.error(
                    f"[HALT] Stage '{stage_name}' failed: {str(e)}"
                )
                raise RuntimeError(
                    f"Pipeline halted at stage '{stage_name}': {str(e)}"
                )
        return wrapper
    return decorator


# ===============================
# LOGGING SETUP
# ===============================

os.makedirs("logs", exist_ok=True)

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

    logging.info(f"Winning thumbnail selected: {best['image_path']}")
    return best


@fail_fast("performance_tracking")
def run_performance_tracking(video_id):
    track_performance(video_id)


@fail_fast("expected_value_projection")
def run_expected_projection():
    run_expected_value_projection()


@fail_fast("adaptive_optimization")
def run_adaptive(video_id, saturated_emotion=None):
    run_adaptive_optimization(
        video_id=video_id,
        saturated_emotion=saturated_emotion
    )


# ===============================
# STATE MACHINE
# ===============================

class PipelineOrchestrator:

    def __init__(self, video_id, title_variants=None, emotion_tag="curiosity"):
        self.video_id = video_id
        self.title_variants = title_variants or []
        self.emotion_tag = emotion_tag
        self.growth_plan = load_growth_plan()
        self.saturated_emotion = None

    def enforce_emotional_governance(self):
        """
        Logs current video emotion and checks for oversaturation.
        If saturated, sets correction signal for adaptive optimizer.
        """
        index = ChannelEmotionalIndex()

        # Log current upload emotion
        index.log_emotion(self.video_id, self.emotion_tag)

        signal = index.governance_signal()

        logging.info(
            f"Emotional distribution check: "
            f"dominant={signal['dominant_emotion']} "
            f"ratio={signal['ratio']}"
        )

        if signal["over_saturated"]:
            logging.warning(
                f"Emotion oversaturated: "
                f"{signal['dominant_emotion']} "
                f"({signal['ratio']})"
            )
            self.saturated_emotion = signal["dominant_emotion"]
        else:
            self.saturated_emotion = None

    def run(self):
        overall_start = time.time()

        try:
            logging.info("========== PIPELINE STARTED ==========")

            # 1️⃣ Manual override
            run_manual_override_check()

            # 2️⃣ Runway discipline
            run_runway_guard()

            # 3️⃣ Cadence enforcement
            run_upload_cadence()

            # 4️⃣ Thumbnail enforcement
            best_thumbnail = run_thumbnail_generation(self.title_variants)
            logging.info(
                f"Thumbnail ready: {best_thumbnail['image_path']}"
            )

            # 5️⃣ Upload assumed complete externally
            logging.info("Upload stage assumed complete.")

            # 6️⃣ Performance tracking
            run_performance_tracking(self.video_id)

            # 7️⃣ Emotional governance (NEW STRUCTURAL CONTROL)
            self.enforce_emotional_governance()

            # 8️⃣ Expected growth projection
            run_expected_projection()

            # 9️⃣ Adaptive optimization (with governance signal)
            run_adaptive(
                self.video_id,
                saturated_emotion=self.saturated_emotion
            )

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
