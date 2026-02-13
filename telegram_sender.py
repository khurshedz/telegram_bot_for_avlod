from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

import requests

from custom_requests import post
from log_setup import *
from secret import TELEGRAM_TOKEN


@dataclass
class SendResult:
    ok: bool
    status_code: Optional[int]
    error: Optional[str] = None
    response_data: Optional[dict[str, Any]] = None


class TelegramClient:
    def __init__(self, token: str = TELEGRAM_TOKEN):
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id: Union[str, int], text: str = 'Не работает =(', parse_mode: str = 'HTML') -> SendResult:
        url = f'{self.base_url}/sendMessage'
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        return self._execute_request(url=url, data=payload, action='send_message', chat_id=chat_id)

    def send_photo(self, chat_id: Union[str, int], photo: Union[str, Path, BinaryIO], text: str,
                   parse_mode: str = 'HTML') -> SendResult:
        url = f"{self.base_url}/sendPhoto"
        data = {'chat_id': chat_id, 'caption': text, 'parse_mode': parse_mode}

        if isinstance(photo, (str, Path)):
            with open(photo, 'rb') as photo_file:
                files = {'photo': photo_file}
                return self._execute_request(url=url, data=data, files=files, action='send_photo', chat_id=chat_id)

        files = {'photo': photo}
        return self._execute_request(url=url, data=data, files=files, action='send_photo', chat_id=chat_id)

    def _execute_request(self, url: str, data: dict[str, Any], action: str, chat_id: Union[str, int],
                         files: Optional[dict[str, Any]] = None) -> SendResult:
        try:
            response = post(url, data=data, files=files)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            status_code = getattr(getattr(err, 'response', None), 'status_code', None)
            result = SendResult(ok=False, status_code=status_code, error=str(err))
            logging.error(
                "telegram_send_failed action=%s chat_id=%s status_code=%s error=%s",
                action,
                chat_id,
                status_code,
                err,
            )
            return result

        response_data = None
        decode_error = None
        try:
            response_data = response.json()
        except ValueError as err:
            decode_error = str(err)

        result = SendResult(
            ok=200 <= response.status_code < 300,
            status_code=response.status_code,
            error=decode_error,
            response_data=response_data,
        )
        logging.info(
            "telegram_send_done action=%s chat_id=%s status_code=%s ok=%s error=%s",
            action,
            chat_id,
            response.status_code,
            result.ok,
            result.error,
        )
        return result


default_telegram_client = TelegramClient()
