import currency
import telegram_sender
import air_q
import datetime
import magnetic_storm
from birth.birthday_check import BirthdayReminder
from secret import CHAT_IDS
from log_setup import *
from config import ESKHATA_PIC_PATH, load_config, validate_startup_paths


def create_block_element(title, content):
    return f"\n<blockquote>{title}</blockquote><pre>{content}</pre>\n"


def get_formatted_currency():
    try:
        cur = currency.get_needed_currency()
        return create_block_element("Курс", cur)
    except Exception as e:
        logging.exception("Could not get currency")
        return ""


def get_formatted_air_quality():
    try:
        air_quality = air_q.get_air_quality()
        return create_block_element("Воздух", air_quality)
    except Exception as e:
        logging.exception("Could not get air quality")
        return ""


def get_formatted_magnetic_storm_level():
    try:
        level = magnetic_storm.get_magnetic_storm_level()
        return create_block_element("магнитосфера", level)
    except Exception as e:
        logging.exception("Could not get magnetic storm level")
        return ""


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
    config = load_config()
    if not validate_startup_paths(config):
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
    except Exception as e:
        logging.exception(f"An exception has occurred: {e}")


def send_birth_message():
    try:
        text, pic = get_birthday_date()
        if not pic:
            logging.info("Skipping birthday photo send: no photo")
            return

        send_photo(photo=pic, text=text)
    except Exception as e:
        logging.exception(f"An error occurred in birth_message: {e}")


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
        try:
            telegram_sender.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logging.exception(f"An error occurred in send_message: {e}")


def send_photo(photo, text):
    if not photo:
        raise ValueError("send_photo expects a non-empty photo")
    if not isinstance(text, str):
        raise ValueError("send_photo expects text as str")

    try:
        telegram_sender.send_photo(photo=photo, text=text)
    except Exception as e:
        logging.exception(f"An error occurred in send_photo: {e}")


if __name__ == '__main__':
    # from random_pics import send_random_pic
    # send_random_pic()
    main()
