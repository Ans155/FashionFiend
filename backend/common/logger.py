"""Logging functionality."""

import logging

# NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, and CRITICAL=50


def create_logger(log_level: int = 20):
    """Creates a logging directory and returns a logger."""
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=log_level,
        # pylint: disable=line-too-long
        format="[%(process)s:%(processName)s:%(threadName)s] %(levelname)s %(asctime)s:%(filename)s:%(funcName)s:%(lineno)d:%(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    return logger