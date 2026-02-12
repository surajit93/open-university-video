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
# LOGGING SETUP
# ===============================

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ===============================
# STATE MACHINE
# ===============================

class PipelineOrchestrator:

    def __init__(self, video_id):
        self.video_id = video_id

    def run(self):
        start_time = time.time()

        try:
            logging.info("Pipeline started.")

            # 1️⃣ Manual Override Check
            if check_manual_override():
                logging.warning("Manual override active. Halting pipeline.")
                return

            # 2️⃣ Runway Protection
            enforce_runway_guard()

            # 3️⃣ Cadence Enforcement
            enforce_upload_cadence()

            # 4️⃣ Upload already assumed completed
            logging.info("Upload stage complete.")

            # 5️⃣ Track Performance
            track_performance(self.video_id)

            # 6️⃣ Expected Growth Projection
            run_expected_value_projection()

            # 7️⃣ Adaptive Optimization
            run_adaptive_optimization(self.video_id)

            duration = time.time() - start_time
            logging.info(f"Pipeline completed in {duration:.2f} seconds.")

        except Exception as e:
            logging.error(f"Pipeline failed: {str(e)}")
            raise


# ===============================
# ENTRY POINT
# ===============================

if __name__ == "__main__":
    orchestrator = PipelineOrchestrator(video_id="latest_video")
    orchestrator.run()
