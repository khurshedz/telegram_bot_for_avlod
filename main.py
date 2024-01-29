import currency
import telegram
import air_q
import datetime
import magnetic_storm
from birth.birthday_check import BirthdayReminder
from secret import CHAT_IDS


def get_formatted_currency():
    return f"\n<blockquote>Курс</blockquote><pre>{currency.get_needed_currency()}</pre>\n"


def get_formatted_air_quality():
    return f"\n<blockquote>Воздух</blockquote><pre>{air_q.get_air_quality()}\n</pre>\n"


def get_formatted_magnetic_storm_level():
    return f'\n<blockquote>магнитосфера</blockquote><pre>{magnetic_storm.get_magnetic_storm_level()}</pre>\n'


def get_formatted_date():
    return f"\n<u>дата:{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')} мск\n</u>"


def get_birthday_date():
    reminder = BirthdayReminder()
    data = reminder.check_birthdays()
    if data:
        text, pic = data
        return f"\n<blockquote>{text}</blockquote>", pic
    else:
        return "", ""


def main():
    text_currency = get_formatted_currency()
    text_air_quality = get_formatted_air_quality()
    storm_level = get_formatted_magnetic_storm_level()
    final_text = text_currency + text_air_quality + storm_level + get_formatted_date()
    send_message(final_text)


def birth_message():
    text, pic = get_birthday_date()
    send_photo(photo=pic, text=text)


def send_message(text):
    for chat_id in CHAT_IDS:
        telegram.send_message(chat_id=chat_id, text=text)


def send_photo(photo, text):
    for chat_id in CHAT_IDS:
        telegram.send_photo(chat_id=chat_id, photo=photo, text=text)


if __name__ == '__main__':
    main()
    birth_message()
