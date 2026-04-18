from typing import Optional, List

from models.YouTube_models import ReportConfig, VideoMetrics
from report_out.print_clicbait_report import print_clickbait_report
from reports.clickbate_reports import clickbait_check
from scv_parser.base_parser import BaseSCVParser


def get_clickbait_report(args) -> Optional[List[List[str]]]:
    """проверка на кликбейт"""
    # Используем ReportConfig для получения колонок
    config = ReportConfig.clickbait_config()

    parser = BaseSCVParser(args.files, config.columns)

    videos: List[VideoMetrics] = clickbait_check(parser)

    if not videos:
        return None

    # формат для таблицы
    results = [video.to_table_row() for video in videos]

    print_clickbait_report(results, config.columns)

    return results
