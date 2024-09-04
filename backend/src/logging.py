import logging
import sys

from .config import settings


class Logger:
    logger: logging.Logger = None

    def __init__(self, name) -> None:
        if not Logger.logger:
            Logger.logger = self._init_logger(name)

    def _init_logger(self, name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(
            fmt="%(asctime)-23s | %(levelname)-8s | %(name)-16s | %(message)s"
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.setLevel(settings.LOG_LEVEL)

        return logger
