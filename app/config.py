import os

class Config:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    BIRTH_DIR = os.path.join(BASE_PATH, 'birth_data')
    LOG_DIR = os.path.join(BASE_PATH, 'logs')
    
    TELEGRAM_TOKEN = ''  # Add your Telegram bot token here
    CHAT_IDS = []  # Add chat IDs here
    API_KEYS = {
        'iq_air': '',
        'weather': '',
    }
