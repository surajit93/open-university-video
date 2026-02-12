import logging
import json
import os
import time


def setup_logger(name, filename):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(f"logs/{filename}")
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_event(logger, module, event, extra=None):
    log_entry = {
        "timestamp": time.time(),
        "module": module,
        "event": event
    }

    if extra:
        log_entry.update(extra)

    logger.info(json.dumps(log_entry))
