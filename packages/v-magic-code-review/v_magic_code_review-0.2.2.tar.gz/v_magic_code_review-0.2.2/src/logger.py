import sys

from loguru import logger


def set_logging_level(debug: bool) -> None:
    level = "DEBUG" if debug else "INFO"
    logger.remove()
    logger.add(sys.stdout, level=level, format="{time} - {level} - {message}")
