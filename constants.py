# scripts/constants.py
# CENTRALIZED CONSTANTS — single source of truth
# Used by: generate_mcq.py, publish_mcq.py, upload_youtube.py, thumbnails, descriptions

from pathlib import Path
import json

# =========================
# PATHS
# =========================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DONATIONS_FILE = PROJECT_ROOT / "donations.json"
CHANNEL_META_FILE = PROJECT_ROOT / "channel.json"

# =========================
# LOADERS
# =========================

def load_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default if default is not None else {}

# =========================
# DONATIONS
# =========================

DONATIONS = load_json(DONATIONS_FILE, {})

PAYPAL_ID = DONATIONS.get("paypal_id", "")
DONATION_TITLE = DONATIONS.get(
    "title",
    "Please Donate for our Hardwork"
)
DONATION_SUBTITLE = DONATIONS.get(
    "subtitle",
    "Right contribution shows your respect for lesson / dedication"
)

DONATION_BANNER_TEXT = DONATIONS.get(
    "banner_text",
    "Please consider donating before attempting this test."
)

GPAY_QR_REL_PATH = DONATIONS.get(
    "gpay_qr_path",
    "payment/gpay/qr.png"
)

# =========================
# CHANNEL / COURSE META
# =========================

CHANNEL_META = load_json(CHANNEL_META_FILE, {})

CHANNEL_NAME = CHANNEL_META.get("channel_name", "Open Media University")
COURSE_NAME = CHANNEL_META.get("course_name", "")
DEFAULT_TAGS = CHANNEL_META.get("default_tags", [])

CHANNEL_FOOTER = CHANNEL_META.get(
    "channel_footer",
    "📺 Subscribe for more university-style lectures.\n"
    "📚 New lessons published regularly."
)

# =========================
# YOUTUBE DESCRIPTION TEMPLATES
# =========================

YOUTUBE_MCq_SECTION = (
    "\n\n📘 Practice Test (MCQs)\n"
    "Test your understanding of this lecture:\n"
    "{mcq_url}\n\n"
    "⚠️ Note: This test is for learning and self-assessment only."
)

# =========================
# THUMBNAIL TEXT DEFAULTS
# =========================

THUMBNAIL_PRIMARY_TEXT = CHANNEL_META.get(
    "thumbnail_primary",
    "University Lecture"
)

THUMBNAIL_SECONDARY_TEXT = CHANNEL_META.get(
    "thumbnail_secondary",
    "Full Course on Channel"
)
