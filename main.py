import currency
import telegram
import air_q
import datetime
import magnetic_storm
from birth.birthday_check import BirthdayReminder
from secret import CHAT_IDS
from log_setup import *


def create_block_element(title, content):
    return f"\n<blockquote>{title}</blockquote><pre>{content}</pre>\n"


def get_formatted_currency():
    try:
        cur = currency.get_needed_currency()
        return create_block_element("Курс", cur)
    except Exception as e:
        logging.exception("Could not get currency")


def get_formatted_air_quality():
    try:
        air_quality = air_q.get_air_quality()
        return create_block_element("Воздух", air_quality)
    except Exception as e:
        logging.exception("Could not get air quality")


def get_formatted_magnetic_storm_level():
    try:
        level = magnetic_storm.get_magnetic_storm_level()
        return create_block_element("магнитосфера", level)
    except Exception as e:
        logging.exception("Could not get magnetic storm level")


def get_formatted_date():
    date = datetime.datetime.now().strftime('%d_%m_%Y %H:%M')
    return f"\n#дата_{date} мск\n #отабот"


def get_birthday_date():
    reminder = BirthdayReminder()
    try:
        data = reminder.check_birthdays()
        if data:
            text, pic = data
            return create_block_element(text, ""), pic
        else:
            return "", ""
    except Exception as e:
        logging.exception("Could not get birthday date")


def main():
    try:
        text_currency = get_formatted_currency()
        text_air_quality = get_formatted_air_quality()
        storm_level = get_formatted_magnetic_storm_level()
        final_text = text_currency + text_air_quality + storm_level + get_formatted_date()
        send_message(final_text)
        birth_message()
    except Exception as e:
        logging.exception(f"An exception has occurred: {e}")


def birth_message():
    try:
        text, pic = get_birthday_date()
        send_photo(photo=pic, text=text)
    except Exception as e:
        logging.exception(f"An error occurred in birth_message: {e}")


def send_message(text):
    for chat_id in CHAT_IDS:
        try:
            telegram.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logging.exception(f"An error occurred in send_message: {e}")


def send_photo(photo, text):
        try:
            if photo and text:  # ensures photo and text are not None or an empty string
                telegram.send_photo(photo=photo, text=text)
        except Exception as e:
            logging.exception(f"An error occurred in send_photo: {e}")


if __name__ == '__main__':
    main()
