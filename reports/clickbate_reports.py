"""создание конкретных отчетов по ютуб видео."""

import argparse
from typing import List

from core.logger import logger
from models.YouTube_models import VideoMetrics
from scv_parser.base_parser import BaseSCVParser

parser = argparse.ArgumentParser(description="проверка на кликбейт")
parser.add_argument(
    "--files", nargs="+", required=True, help="Список CSV файлов для анализа"
)
parser.add_argument("--report", required=True, help="Тип отчёта")


def clickbait_check(parser_param: BaseSCVParser) -> List[VideoMetrics]:
    """проверка на кликбейт."""
    data = parser_param.get_selected_columns_by_names()

    videos = []
    for row in data:
        try:

            title = row.get("title")
            ctr_value = row.get("ctr")
            retention_value = row.get("retention_rate")

            if title is None or ctr_value is None or retention_value is None:
                continue

            video = VideoMetrics(
                title=row["title"],
                ctr=float(row["ctr"]),
                retention_rate=float(row["retention_rate"]),
            )

            if video.is_clickbait:
                videos.append(video)

        except (ValueError, KeyError) as e:
            logger.error("Ошибка при обработке строки %s: %s", row, e)
            continue
        except ValueError as e:
            logger.error("Ошибка валидации данных: %s", e)
            continue

    # Сортируем по убыванию CTR
    videos.sort(key=lambda x: x.ctr, reverse=True)

    return videos
