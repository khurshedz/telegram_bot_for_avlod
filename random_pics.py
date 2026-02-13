from pathlib import Path

from birth.birthday_check import BirthdayReminder
from config import RANDOM_PIC_PATH
from telegram_sender import send_photo


def send_random_pic():
    pic = BirthdayReminder().get_random_file(RANDOM_PIC_PATH)
    file_name = Path(pic).name
    send_photo(photo=pic, text=f"Случайное фото {file_name}")


if __name__ == '__main__':
    send_random_pic()
