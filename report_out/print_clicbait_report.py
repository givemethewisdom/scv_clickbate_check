"формирования табилц для отчетов по студентам."

from typing import List

from tabulate import tabulate


def print_clickbait_report(results: List[List[str]], headers: List[str]) -> None:
    """Выводит отчёт в формате таблицы"""
    if not results:
        return

    # Создаем таблицу
    table = tabulate(results, headers=headers, tablefmt="grid")

    print(table)
