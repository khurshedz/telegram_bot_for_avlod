import logging

from config import validate_startup_paths
from log_setup import setup_logging
from services.eskhata_report import EskhataReportService
from services.report_builder import DailyReportBuilder
from services.telegram_notifier import TelegramNotifier


logger = setup_logging()


def main():
    if not validate_startup_paths():
        logger.error("Приложение остановлено: обязательные пути недоступны.")
        return

    report_builder = DailyReportBuilder(logger=logger)
    notifier = TelegramNotifier(logger=logger)
    eskhata_report_service = EskhataReportService(logger=logger)

    try:
        final_text = report_builder.build_daily_report()
        if final_text.strip():
            notifier.send_text(final_text)
        else:
            logger.info("Skipping Telegram send: final text is empty or whitespace")

        birthday_text, birthday_pic = report_builder.get_birthday_payload()
        if birthday_pic:
            notifier.send_photo(photo=birthday_pic, text=birthday_text)
        else:
            logger.info("Skipping birthday photo send: no photo")

        eskhata_photo, eskhata_text = eskhata_report_service.build()
        notifier.send_photo(photo=eskhata_photo, text=eskhata_text)
    except Exception:
        logger.exception("An exception has occurred in main")


if __name__ == '__main__':
    main()
