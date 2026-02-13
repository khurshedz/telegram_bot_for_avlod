import logging

from config import LOG_FILE_PATH

LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

handler = logging.FileHandler(LOG_FILE_PATH, 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler], level=logging.DEBUG)
