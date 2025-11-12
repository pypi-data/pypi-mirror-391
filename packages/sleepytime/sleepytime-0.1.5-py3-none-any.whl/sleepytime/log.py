"""
Base logging infra for Sleepytime.
"""
import logging
import logging.handlers
import os
from functools import cache
from pathlib import Path

from appdirs import user_log_dir

FORMATTER = (
    "%(asctime)s - [%(process)d] - %(name)s:%(lineno)d - %(levelname)s - %(message)s"
)

LOG_DIRECTORY = Path(user_log_dir("sleepytime"))
LATEST_LOG_FILE = LOG_DIRECTORY / "sleepytime.log"


@cache
def setup_logging() -> logging.Logger:
    """
    Called once to setup the base logging. It is cached to ensure it can only do its thing once.
    """
    base_logger = logging.getLogger("sleepytime")
    base_logger.setLevel(os.environ.get("SLEEPYTIME_LOG_LEVEL", "INFO"))

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMATTER))
    base_logger.addHandler(sh)

    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    rfh = logging.handlers.RotatingFileHandler(
        filename=LATEST_LOG_FILE,
        maxBytes=1024 * 1024 * 8,
        backupCount=5,
        delay=True,
    )
    rfh.setFormatter(logging.Formatter(FORMATTER))
    base_logger.addHandler(rfh)

    return base_logger
