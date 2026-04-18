"базовый класс для парса любых отчетов."

import csv
from core.logger import logger


class BaseSCVParser:

    def __init__(self, file_paths, column_names):
        self.file_paths = file_paths
        self.column_names = column_names

    def _check_all_columns_exist(self, header: list, file_path: str) -> bool:
        """check for all columns in file"""
        for col_name in self.column_names:
            if col_name not in header:
                logger.error(
                    "Колонка '%s' не найдена в файле %s. Файл будет пропущен.",
                    col_name,
                    file_path,
                )
                return False
        return True

    def get_selected_columns_by_names(self) -> list[dict]:
        """get selected columns from list of scv files"""
        all_data = []

        for file_path in self.file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    header = next(reader)

                    if not self._check_all_columns_exist(header, file_path):
                        continue

                    column_indices = [
                        header.index(col_name) for col_name in self.column_names
                    ]

                    for row in reader:
                        data_row = {}
                        for idx, col_name in zip(column_indices, self.column_names):
                            data_row[col_name] = row[idx]
                        all_data.append(data_row)

            except FileNotFoundError:
                logger.error("файл %s не найден", file_path)
            except Exception as e:
                logger.error("Ошибка при обработке файла %s: %s", file_path, str(e))

        return all_data
