# scripts/youtube_auth.py

import os
import pickle
import time
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError


SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]

TOKEN_PATH = "config/youtube_token.pkl"
CLIENT_SECRET_PATH = "config/client_secret.json"

# Optional: escalate wait if quota exceeded
QUOTA_BACKOFF_SECONDS = 900  # 15 min hard backoff


def _save_credentials(creds):
    os.makedirs("config", exist_ok=True)
    with open(TOKEN_PATH, "wb") as token:
        pickle.dump(creds, token)


def _load_credentials():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            return pickle.load(token)
    return None


def _perform_oauth_flow():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    _save_credentials(creds)
    return creds


def get_authenticated_credentials(force_reauth=False):
    """
    Production-grade credential handler:
    - Persistent token storage
    - Auto refresh
    - Quota-aware backoff
    - Controlled re-auth fallback
    """

    creds = None

    if not force_reauth:
        creds = _load_credentials()

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_credentials(creds)
        except Exception as refresh_error:
            logging.warning(
                f"[AUTH] Token refresh failed: {refresh_error}. Forcing re-auth."
            )
            creds = None

    # If still invalid → full OAuth
    if not creds or not creds.valid:
        creds = _perform_oauth_flow()

    return creds


def handle_quota_error(error: HttpError):
    """
    Escalation logic for quota exhaustion.
    Prevents silent retry storms.
    """

    error_str = str(error)

    if "quotaExceeded" in error_str or "userRateLimitExceeded" in error_str:
        logging.error("[AUTH] YouTube API quota exceeded. Entering hard backoff.")
        time.sleep(QUOTA_BACKOFF_SECONDS)
        raise RuntimeError(
            "YouTube API quota exceeded. Pipeline paused for protection."
        )

    raise error
