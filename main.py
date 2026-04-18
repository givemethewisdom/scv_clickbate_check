"""точка входа."""

from core.logger import logger
from get_report.get_youtube_report import get_clickbait_report

from reports.clickbate_reports import parser

# регистрацуия отчетов
YouTube_REPORTS = {"clickbait": get_clickbait_report}


def main():
    """Точка входа"""
    args = parser.parse_args()
    logger.info("Получены файлы: %s", args.files)
    logger.info("Тип отчёта: %s", args.report)

    if args.report not in YouTube_REPORTS:
        logger.error("Ошибка: отчёт %s не поддерживается", args.report)
        logger.info(f"Доступные отчёты: {', '.join(YouTube_REPORTS.keys())}")
        return

    YouTube_REPORTS[args.report](args)


if __name__ == "__main__":
    main()
