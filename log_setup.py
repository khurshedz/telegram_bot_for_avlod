import logging
from config import BASE_PATH

logname = '/home/spac/Logs/telegram/telebot.log'

# Set up logging
handler = logging.FileHandler(logname, 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logging.basicConfig(handlers=[handler], level=logging.DEBUG)
