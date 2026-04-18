# core/logger.py
"""логгер с записью ошибок в файл"""

import logging
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent  # Поднимаемся на уровень выше из core/
LOGS_DIR = ROOT_DIR / "logs"

LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(),
        # В файл только ERROR
        logging.FileHandler(
            LOGS_DIR / f"{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"
        ),
    ],
)

for handler in logging.root.handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.ERROR)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
    elif isinstance(handler, logging.StreamHandler):
        handler.setLevel(logging.DEBUG)


def get_logger(name=None):
    return logging.getLogger(name)


logger = get_logger()
