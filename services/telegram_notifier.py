import logging

import telegram_sender
from secret import CHAT_IDS


class TelegramNotifier:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def send_text(self, text: str) -> None:
        if not isinstance(text, str):
            raise ValueError("send_text expects text as str")

        for chat_id in CHAT_IDS:
            try:
                telegram_sender.send_message(chat_id=chat_id, text=text)
            except Exception:
                self.logger.exception("An error occurred in send_text for chat_id=%s", chat_id)

    def send_photo(self, photo, text: str) -> None:
        if not photo:
            raise ValueError("send_photo expects a non-empty photo")
        if not isinstance(text, str):
            raise ValueError("send_photo expects text as str")

        try:
            telegram_sender.send_photo(photo=photo, text=text)
        except Exception:
            self.logger.exception("An error occurred in send_photo")
