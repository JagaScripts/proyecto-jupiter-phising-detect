import logging
import os
from logging.handlers import RotatingFileHandler
from config import get_log_dir


def setup_logging() -> None:
    logger = logging.getLogger("dominio")
    if logger.handlers:
        return

    logger.setLevel(logging.DEBUG)

    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    debug_file = os.path.join(log_dir, "debug.log")
    debug_handler = RotatingFileHandler(debug_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    warning_file = os.path.join(log_dir, "warning.log")
    warning_handler = RotatingFileHandler(warning_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)
    logger.addHandler(warning_handler)
