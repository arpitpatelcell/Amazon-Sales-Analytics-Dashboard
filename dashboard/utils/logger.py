"""
utils/logger.py
Centralized logging setup.

Why this matters (industry practice):
Instead of using print() statements scattered across the app — which
disappear once the terminal closes — a proper logger writes timestamped,
leveled messages (INFO, WARNING, ERROR) to both the console and a log
file. This makes debugging production issues far easier.
"""

import logging
import os
import sys

_LOGGER_NAME = "amazon_dashboard"


def get_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Returns a configured logger instance. Safe to call multiple times —
    handlers are only attached once.
    """
    logger = logging.getLogger(_LOGGER_NAME)

    if logger.handlers:
        # Already configured — avoid duplicate handlers on Streamlit reruns
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (best-effort — don't crash the app if the filesystem is read-only,
    # e.g. on some cloud deployments)
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not create log file — continuing with console logging only.")

    return logger
