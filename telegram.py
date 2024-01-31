import logging
import requests
from secret import TOKEN
import log_setup

log_setup.setup_logger()


def send_message(chat_id, text='Не работает =(', parse_mode='HTML'):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        return errh
    except requests.exceptions.RequestException as err:
        logger.error(f"Error: {err}")
        return err

    logger.info(f"Message sent with response code {response.status_code}")

    return response.json()


def send_photo(chat_id, photo, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    files = {'photo': open(photo, 'rb') if isinstance(photo, str) else photo.read()}
    data = {'chat_id': chat_id, 'caption': text, 'parse_mode': 'HTML'}

    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        return errh
    except requests.exceptions.RequestException as err:
        logger.error(f"Error: {err}")
        return err

    logger.info(f"Photo sent with response code {response.status_code}")

    return response.json()