# pipeline/orchestrator.py

import time
import logging
import os
import sqlite3
import yaml
import datetime

from scripts.upload_cadence_enforcer import enforce_upload_cadence
from scripts.runway_guard import enforce_runway_guard
from scripts.performance_tracker import track_performance
from scripts.adaptive_optimizer import run_adaptive_optimization
from scripts.expected_value_model import run_expected_value_projection
from scripts.manual_override import check_manual_override
from scripts.thumbnail_variation_generator import ThumbnailVariationGenerator
from scripts.channel_emotional_index import ChannelEmotionalIndex
from scripts.style_evolution_manager import StyleEvolutionManager
from scripts.session_depth_optimizer import SessionDepthOptimizer
from scripts.packaging_guard import enforce_cooling_period
from config.channel_growth_plan import load_growth_plan


# ============================================================
# GLOBAL FAIL FAST
# ============================================================

def fail_fast(stage_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                logging.info(f"[START] {stage_name}")
                start = time.time()

                result = func(*args, **kwargs)

                duration = time.time() - start
                logging.info(f"[END] {stage_name} | {duration:.2f}s")
                return result

            except Exception as e:
                logging.error(f"[HALT] {stage_name} failed: {str(e)}")
                raise RuntimeError(
                    f"Pipeline halted at stage '{stage_name}': {str(e)}"
                )
        return wrapper
    return decorator


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def get_total_uploads():
    db_path = "data/performance.db"
    if not os.path.exists(db_path):
        return 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(DISTINCT video_id)
    FROM video_performance
    """)

    count = cursor.fetchone()[0] or 0
    conn.close()
    return count


@fail_fast("style_evolution_check")
def run_style_evolution():
    total_uploads = get_total_uploads()

    manager = StyleEvolutionManager()

    if manager.should_refresh(total_uploads) and total_uploads != 0:
        logging.info(f"[STYLE] Evolution triggered at #{total_uploads}")

        config_path = "config/channel_config.yaml"

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        updated_config = manager.evolve_style(config)

        with open(config_path, "w") as f:
            yaml.safe_dump(updated_config, f)

        logging.info(
            f"[STYLE] New accent_color="
            f"{updated_config.get('accent_color')}"
        )
    else:
        logging.info(f"[STYLE] No evolution. Uploads={total_uploads}")


@fail_fast("session_depth_optimization")
def run_session_depth_optimization():
    optimizer = SessionDepthOptimizer()

    avg_depth = optimizer.average_session_depth()
    clusters = optimizer.prioritize_clusters()

    logging.info(f"[SESSION] Avg depth={avg_depth}")

    if clusters:
        top_cluster = clusters[0][0]
        logging.info(f"[SESSION] Promote cluster: {top_cluster}")
        return top_cluster

    logging.info("[SESSION] No cluster data.")
    return None


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

    logging.info(f"[THUMBNAIL] Selected: {best['image_path']}")
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


class PipelineOrchestrator:

    def __init__(self, video_id, title_variants=None, emotion_tag="curiosity"):
        self.video_id = video_id
        self.title_variants = title_variants or []
        self.emotion_tag = emotion_tag
        self.growth_plan = load_growth_plan()
        self.saturated_emotion = None
        self.cluster_recommendation = None
        self.created_timestamp = datetime.datetime.now()

    def enforce_emotional_governance(self):
        index = ChannelEmotionalIndex()

        index.log_emotion(self.video_id, self.emotion_tag)
        signal = index.governance_signal()

        logging.info(
            f"[EMOTION] dominant={signal['dominant_emotion']} "
            f"ratio={signal['ratio']}"
        )

        if signal["over_saturated"]:
            logging.warning(
                f"[EMOTION] Oversaturated: "
                f"{signal['dominant_emotion']}"
            )
            self.saturated_emotion = signal["dominant_emotion"]
        else:
            self.saturated_emotion = None

    def run(self):
        overall_start = time.time()

        try:
            logging.info("========== PIPELINE STARTED ==========")

            enforce_cooling_period(self.created_timestamp)

            run_manual_override_check()
            run_runway_guard()
            run_upload_cadence()

            best_thumbnail = run_thumbnail_generation(self.title_variants)
            logging.info(f"[THUMBNAIL READY] {best_thumbnail['image_path']}")

            logging.info("Upload stage assumed complete.")

            run_performance_tracking(self.video_id)

            run_style_evolution()

            self.cluster_recommendation = run_session_depth_optimization()

            self.enforce_emotional_governance()

            run_expected_projection()

            run_adaptive(
                self.video_id,
                saturated_emotion=self.saturated_emotion
            )

            total_duration = time.time() - overall_start

            logging.info(
                f"========== PIPELINE COMPLETE "
                f"{total_duration:.2f}s =========="
            )

        except Exception as e:
            logging.error(f"PIPELINE FAILED: {str(e)}")
            raise


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
