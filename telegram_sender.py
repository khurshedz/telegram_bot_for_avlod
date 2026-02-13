from custom_requests import post

import requests
from secret import TELEGRAM_TOKEN, CHAT_IDS
from log_setup import *


def send_message(chat_id, text='Не работает =(', parse_mode='HTML'):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}

    try:
        response = post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
        return errh
    except requests.exceptions.RequestException as err:
        logging.error(f"Error: {err}")
        return err

    logging.info(f"Message sent with response code {response.status_code}")

    return response.json()


def send_photo(photo, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    for chat_id in CHAT_IDS:
        data = {'chat_id': chat_id, 'caption': text, 'parse_mode': 'HTML'}

        try:
            if isinstance(photo, str):
                with open(photo, 'rb') as f:
                    files = {'photo': f}
                    response = post(url, files=files, data=data)
            else:
                files = {'photo': photo}
                response = post(url, files=files, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.error(f"HTTP Error: {errh}")
            continue
        except requests.exceptions.RequestException as err:
            logging.error(f"Error: {err}")
            continue

        success = 200 <= response.status_code < 300
        logging.info(f'Photo {photo} sent. Success: {success}')

        try:
            resp = response.json()
        except ValueError as err:
            logging.error(f"JSON decode error: {err}")
            continue

        logging.info(f'{resp.get("resp", "no resp")}: {resp.get("error_code","no err code")}')
