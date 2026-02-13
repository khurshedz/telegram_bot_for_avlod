import datetime
import logging

import air_q
import currency
import magnetic_storm
from birth.birthday_check import BirthdayReminder


class DailyReportBuilder:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @staticmethod
    def create_block_element(title: str, content: str) -> str:
        return f"\n<blockquote>{title}</blockquote><pre>{content}</pre>\n"

    def _safe_block(self, title: str, producer, error_message: str) -> str:
        try:
            content = producer()
            return self.create_block_element(title, content)
        except Exception:
            self.logger.exception(error_message)
            return ""

    def get_formatted_currency(self) -> str:
        return self._safe_block("Курс", currency.get_needed_currency, "Could not get currency")

    def get_formatted_air_quality(self) -> str:
        return self._safe_block("Воздух", air_q.get_air_quality, "Could not get air quality")

    def get_formatted_magnetic_storm_level(self) -> str:
        return self._safe_block(
            "магнитосфера",
            magnetic_storm.get_magnetic_storm_level,
            "Could not get magnetic storm level",
        )

    @staticmethod
    def get_formatted_date() -> str:
        date = datetime.datetime.now().strftime("%d_%m_%Y %H:%M")
        return f"\n#дата_{date} мск\n #отабот"

    def build_daily_report(self) -> str:
        sections = [
            self.get_formatted_currency(),
            self.get_formatted_air_quality(),
            self.get_formatted_magnetic_storm_level(),
            self.get_formatted_date(),
        ]
        return "".join(sections)

    def get_birthday_payload(self) -> tuple[str, str]:
        reminder = BirthdayReminder()
        try:
            data = reminder.check_birthdays()
            if not data:
                return "", ""

            text, pic = data
            return self.create_block_element(text, ""), pic
        except Exception:
            self.logger.exception("Could not get birthday date")
            return "", ""
