# scripts/packaging_guard.py

import datetime


COOLING_SECONDS = 86400  # 24 hours


def enforce_cooling_period(created_timestamp):
    """
    created_timestamp must be datetime object
    """
    now = datetime.datetime.now()
    delta = (now - created_timestamp).total_seconds()

    if delta < COOLING_SECONDS:
        remaining = COOLING_SECONDS - delta
        raise RuntimeError(
            f"Packaging cooling active. {remaining/3600:.2f} hours remaining."
        )
