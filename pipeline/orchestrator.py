import time
import logging

from scripts.upload_cadence_enforcer import enforce_upload_cadence
from scripts.runway_guard import enforce_runway_guard
from scripts.performance_tracker import track_performance
from scripts.adaptive_optimizer import run_adaptive_optimization
from scripts.expected_value_model import run_expected_value_projection
from scripts.manual_override import check_manual_override
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


@fail_fast("performance_tracking")
def run_performance_tracking(video_id):
    track_performance(video_id)


@fail_fast("expected_value_projection")
def run_expected_projection():
    run_expected_value_projection()


@fail_fast("adaptive_optimization")
def run_adaptive(video_id):
    run_adaptive_optimization(video_id)


# ===============================
# STATE MACHINE
# ===============================

class PipelineOrchestrator:

    def __init__(self, video_id):
        self.video_id = video_id
        self.growth_plan = load_growth_plan()

    def run(self):
        overall_start = time.time()

        try:
            logging.info("========== PIPELINE STARTED ==========")

            # 1️⃣ Manual Override Check
            run_manual_override_check()

            # 2️⃣ Runway Protection
            run_runway_guard()

            # 3️⃣ Upload Cadence Enforcement
            run_upload_cadence()

            # 4️⃣ Upload assumed completed externally
            logging.info("Upload stage assumed complete.")

            # 5️⃣ Track Performance
            run_performance_tracking(self.video_id)

            # 6️⃣ Expected Growth Projection
            run_expected_projection()

            # 7️⃣ Adaptive Optimization
            run_adaptive(self.video_id)

            total_duration = time.time() - overall_start
            logging.info(
                f"========== PIPELINE COMPLETED SUCCESSFULLY "
                f"in {total_duration:.2f}s =========="
            )

        except Exception as e:
            logging.error(f"PIPELINE FAILED: {str(e)}")
            raise


# ===============================
# ENTRY POINT
# ===============================

if __name__ == "__main__":
    orchestrator = PipelineOrchestrator(video_id="latest_video")
    orchestrator.run()
