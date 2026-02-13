from pathlib import Path
from typing import BinaryIO, Iterable, Union

from log_setup import *
from telegram_sender import SendResult, TelegramClient


class TelegramBroadcaster:
    def __init__(self, chat_ids: Iterable[Union[str, int]], client: TelegramClient):
        self.chat_ids = list(chat_ids)
        self.client = client

    def send_to_all_chats(self, text: str, parse_mode: str = 'HTML') -> list[SendResult]:
        results = [
            self.client.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            for chat_id in self.chat_ids
        ]
        self._log_summary(action='send_message', results=results)
        return results

    def send_photo_to_all_chats(self, photo: Union[str, Path, BinaryIO], text: str,
                                parse_mode: str = 'HTML') -> list[SendResult]:
        results = [
            self.client.send_photo(chat_id=chat_id, photo=photo, text=text, parse_mode=parse_mode)
            for chat_id in self.chat_ids
        ]
        self._log_summary(action='send_photo', results=results)
        return results

    @staticmethod
    def _log_summary(action: str, results: list[SendResult]) -> None:
        success_count = sum(1 for result in results if result.ok)
        logging.info(
            "telegram_broadcast_done action=%s total=%s success=%s failed=%s",
            action,
            len(results),
            success_count,
            len(results) - success_count,
        )
