import logging
import os
import tempfile
from pathlib import Path
import uuid
import sys


class CustomFormatter(logging.Formatter):
    """Logging colored formatter"""

    grey = "\x1b[38;21m"
    green = "\x1b[92m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, format):
        """Initializes the class

        Args:
            format: format of logger
        """
        super().__init__()
        self.fmt = format
        self.FORMATS = {
            logging.DEBUG: self.green + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        """Given a record, format it

        Args:
            record: the record

        Returns:
            the formatted record
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def configure_logger(name, fmt=None, log_level=None):
    sys.stdout.reconfigure(encoding="utf-8")

    logger = logging.getLogger(name)

    # Determine log level from parameter, environment variable, or default to INFO
    if log_level is None:
        log_level = os.getenv("XCHAT_LOG_LEVEL", "INFO").upper()

    # Convert string to logging level
    numeric_level = getattr(logging, log_level, logging.INFO)
    logger.setLevel(numeric_level)
    logger.propagate = False

    if fmt is None:
        fmt = "%(asctime)s | %(levelname)s | %(name)s %(lineno)d | %(message)s"

    # Stream (console) handler — ensure UTF-8
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(numeric_level)
    stdout_handler.setFormatter(CustomFormatter(fmt))

    logs_path = os.getenv("LOGS_FILE_PATH")
    if logs_path is None:
        logs_path = Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.stochastic.logs"

    Path(logs_path).parent.mkdir(parents=True, exist_ok=True)

    # File handler — explicit UTF-8 encoding
    file_handler = logging.FileHandler(str(logs_path), encoding="utf-8")
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(logging.Formatter(fmt))

    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger
