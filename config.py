import logging
import os
from dataclasses import dataclass
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Config:
    birth_dir: Path
    birth_db_dir: Path
    csv_file_name: Path
    text_file_name: Path
    pic_folder_name: Path
    random_pic_path: Path
    eskhata_pic_path: Path
    log_file_path: Path


def load_config() -> Config:
    birth_dir = Path(os.getenv("BIRTH_DIR", BASE_PATH / "birth"))
    birth_db_dir = Path(os.getenv("BIRTH_DB_DIR", birth_dir / "db"))

    return Config(
        birth_dir=birth_dir,
        birth_db_dir=birth_db_dir,
        csv_file_name=Path(os.getenv("CSV_FILE_NAME", birth_db_dir / "birthdays.csv")),
        text_file_name=Path(os.getenv("TEXT_FILE_NAME", birth_db_dir / "random_text.txt")),
        pic_folder_name=Path(os.getenv("PIC_FOLDER_NAME", birth_dir / "pics")),
        random_pic_path=Path(os.getenv("RANDOM_PIC_PATH", BASE_PATH / "random_pics")),
        eskhata_pic_path=Path(os.getenv("ESKHATA_PIC_PATH", BASE_PATH / "screens/eskhata_currency.png")),
        log_file_path=Path(os.getenv("LOG_FILE_PATH", BASE_PATH / "logs" / "telebot.log")),
    )


_CONFIG = load_config()

BIRTH_DIR = _CONFIG.birth_dir
BIRTH_DB_DIR = _CONFIG.birth_db_dir
CSV_FILE_NAME = _CONFIG.csv_file_name
TEXT_FILE_NAME = _CONFIG.text_file_name
PIC_FOLDER_NAME = _CONFIG.pic_folder_name

RANDOM_PIC_PATH = _CONFIG.random_pic_path
ESKHATA_PIC_PATH = _CONFIG.eskhata_pic_path

LOG_FILE_PATH = _CONFIG.log_file_path


def validate_startup_paths(config: Config | None = None) -> bool:
    config = config or _CONFIG

    required_dirs = {
        "Каталог с данными дней рождения": config.birth_db_dir,
        "Каталог с картинками для поздравлений": config.pic_folder_name,
        "Каталог со случайными картинками": config.random_pic_path,
    }
    required_files = {
        "CSV с днями рождения": config.csv_file_name,
        "Файл с поздравительными текстами": config.text_file_name,
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
