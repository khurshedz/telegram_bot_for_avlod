import datetime

import air_q
import currency
import magnetic_storm
import telegram_sender
from birth.birthday_check import BirthdayReminder
from config import ESKHATA_PIC_PATH, validate_startup_paths
from errors import IntegrationError
from log_setup import *
from secret import CHAT_IDS


def create_block_element(title, content):
    return f"\n<blockquote>{title}</blockquote><pre>{content}</pre>\n"


def get_formatted_currency():
    cur = currency.get_needed_currency()
    return create_block_element("Курс", cur)


def get_formatted_air_quality():
    air_quality = air_q.get_air_quality()
    return create_block_element("Воздух", air_quality)


def get_formatted_magnetic_storm_level():
    level = magnetic_storm.get_magnetic_storm_level()
    return create_block_element("магнитосфера", level)


def get_formatted_date():
    date = datetime.datetime.now().strftime('%d_%m_%Y %H:%M')
    return f"\n#дата_{date} мск\n #отабот"


def get_birthday_date():
    reminder = BirthdayReminder()
    data = reminder.check_birthdays()
    if data:
        text, pic = data
        return create_block_element(text, ""), pic

    return "", ""


def main():
    if not validate_startup_paths():
        logging.error("Приложение остановлено: обязательные пути недоступны.")
        return

    try:
        text_currency = get_formatted_currency()
        text_air_quality = get_formatted_air_quality()
        storm_level = get_formatted_magnetic_storm_level()
        final_text = text_currency + text_air_quality + storm_level + get_formatted_date()
        if not final_text.strip():
            logging.info("Skipping Telegram send: final text is empty or whitespace")
            return

        send_message(final_text)
        send_birth_message()
        send_eskhata_currency()
    except IntegrationError:
        logging.exception("External integration failed")
    except Exception:
        logging.exception("Unexpected error in main orchestration")


def send_birth_message():
    text, pic = get_birthday_date()
    if not pic:
        logging.info("Skipping birthday photo send: no photo")
        return

    send_photo(photo=pic, text=text)


def send_eskhata_currency():
    from currency_eskhata import EskhataScreenshot

    runner = EskhataScreenshot(
        visible=False,
        out_path=str(ESKHATA_PIC_PATH),
        window_size=(780, 720),
    )
    result = runner.run()
    print(result)
    send_photo(str(ESKHATA_PIC_PATH), "Курс по эсхата")


def send_message(text):
    if not isinstance(text, str):
        raise ValueError("send_message expects text as str")

    for chat_id in CHAT_IDS:
        telegram_sender.send_message(chat_id=chat_id, text=text)


def send_photo(photo, text):
    if not photo:
        raise ValueError("send_photo expects a non-empty photo")
    if not isinstance(text, str):
        raise ValueError("send_photo expects text as str")

    telegram_sender.send_photo(photo=photo, text=text)


if __name__ == '__main__':
    # from random_pics import send_random_pic
    # send_random_pic()
    main()
