from pathlib import Path

from birth.birthday_check import BirthdayReminder
from config import RANDOM_PIC_PATH
from secret import CHAT_IDS
from telegram_broadcaster import TelegramBroadcaster
from telegram_sender import default_telegram_client


broadcaster = TelegramBroadcaster(chat_ids=CHAT_IDS, client=default_telegram_client)


def send_random_pic():
    pic = BirthdayReminder().get_random_file(RANDOM_PIC_PATH)
    file_name = Path(pic).name
    broadcaster.send_photo_to_all_chats(photo=pic, text=f"Случайное фото {file_name}")


if __name__ == '__main__':
    send_random_pic()
