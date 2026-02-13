from custom_requests import post

import requests

from errors import IntegrationError
from log_setup import *
from secret import TELEGRAM_TOKEN, CHAT_IDS


def send_message(chat_id, text='Не работает =(', parse_mode='HTML'):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}

    try:
        response = post(url, data=payload)
        response.raise_for_status()
        logging.info(f"Message sent with response code {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as exc:
        raise IntegrationError(f"Failed to send Telegram message to chat_id={chat_id}") from exc
    except ValueError as exc:
        raise IntegrationError("Failed to decode Telegram sendMessage response") from exc


def send_photo(photo, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    for chat_id in CHAT_IDS:
        data = {'chat_id': chat_id, 'caption': text, 'parse_mode': 'HTML'}

        try:
            if isinstance(photo, str):
                with open(photo, 'rb') as file_handle:
                    files = {'photo': file_handle}
                    response = post(url, files=files, data=data)
            else:
                files = {'photo': photo}
                response = post(url, files=files, data=data)

            response.raise_for_status()
            logging.info(f'Photo {photo} sent to chat_id={chat_id}.')
            resp = response.json()
            logging.info(f'{resp.get("resp", "no resp")}: {resp.get("error_code", "no err code")}')
        except OSError as exc:
            raise IntegrationError(f"Failed to read photo from path: {photo}") from exc
        except requests.exceptions.RequestException as exc:
            raise IntegrationError(f"Failed to send Telegram photo to chat_id={chat_id}") from exc
        except ValueError as exc:
            raise IntegrationError("Failed to decode Telegram sendPhoto response") from exc
