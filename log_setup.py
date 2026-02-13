import logging

from config import LOG_FILE_PATH


def setup_logging() -> logging.Logger:
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.FileHandler(LOG_FILE_PATH, 'a', 'utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)

    return logging.getLogger(__name__)
