import os

from birth.birthday_check import BirthdayReminder
from config import RANDOM_PIC_PATH
from main import send_photo
from log_setup import setup_logger

# Setup logging
setup_logger()
def send_random_pic():
    pic = BirthdayReminder().get_random_file(RANDOM_PIC_PATH)
    send_photo(photo=pic, text=f"Случайное фото {pic.split('random_pics/')[-1]}")
    logging.info(f'Photo {pic} sent.')
    os.remove(pic)
    logging.info(f'Photo {pic} deleted.')

if __name__ == '__main__':
    send_random_pic()