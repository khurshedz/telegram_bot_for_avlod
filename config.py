import logging
import os
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent

BIRTH_DIR = Path(os.getenv("BIRTH_DIR", BASE_PATH / "birth"))
BIRTH_DB_DIR = Path(os.getenv("BIRTH_DB_DIR", BIRTH_DIR / "db"))
CSV_FILE_NAME = Path(os.getenv("CSV_FILE_NAME", BIRTH_DB_DIR / "birthdays.csv"))
TEXT_FILE_NAME = Path(os.getenv("TEXT_FILE_NAME", BIRTH_DB_DIR / "random_text.txt"))
PIC_FOLDER_NAME = Path(os.getenv("PIC_FOLDER_NAME", BIRTH_DIR / "pics"))

RANDOM_PIC_PATH = Path(os.getenv("RANDOM_PIC_PATH", BASE_PATH / "random_pics"))
ESKHATA_PIC_PATH = Path(os.getenv("ESKHATA_PIC_PATH", BASE_PATH / "screens/eskhata_currency.png"))

LOG_FILE_PATH = Path(os.getenv("LOG_FILE_PATH", BASE_PATH / "logs" / "telebot.log"))


def validate_startup_paths() -> bool:
    required_dirs = {
        "Каталог с данными дней рождения": BIRTH_DB_DIR,
        "Каталог с картинками для поздравлений": PIC_FOLDER_NAME,
        "Каталог со случайными картинками": RANDOM_PIC_PATH,
    }
    required_files = {
        "CSV с днями рождения": CSV_FILE_NAME,
        "Файл с поздравительными текстами": TEXT_FILE_NAME,
    }

    is_valid = True

    for name, path in required_dirs.items():
        if not path.exists():
            logging.error("%s не найден: %s", name, path)
            is_valid = False
        elif not path.is_dir():
            logging.error("%s должен быть директорией: %s", name, path)
            is_valid = False

    for name, path in required_files.items():
        if not path.exists():
            logging.error("%s не найден: %s", name, path)
            is_valid = False
        elif not path.is_file():
            logging.error("%s должен быть файлом: %s", name, path)
            is_valid = False

    if not is_valid:
        logging.error("Проверка путей при старте завершилась с ошибками.")
    else:
        logging.info("Проверка путей при старте успешно пройдена.")

    return is_valid

validate_startup_paths()