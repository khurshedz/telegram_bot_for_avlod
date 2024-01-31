import logging


def setup_logger():
    # Set up logging
    handler = logging.FileHandler('telebot.log', 'a', 'utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=logging.DEBUG)
