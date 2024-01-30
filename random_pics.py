from birth.birthday_check import BirthdayReminder
from config import RANDOM_PIC_PATH
from telegram import send_photo


def send_random_pic():
    pic = BirthdayReminder().get_random_file(RANDOM_PIC_PATH)
    send_photo(photo=pic, text=f"Случайное фото {pic.split('random_pics/')[-1]}")


if __name__ == '__main__':
    send_random_pic()
