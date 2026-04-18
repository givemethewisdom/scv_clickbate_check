import unittest
from unittest.mock import patch, mock_open, MagicMock
from parameterized import parameterized
import csv
from io import StringIO

from scv_parser.base_parser import BaseSCVParser


class TestBaseSCVParser(unittest.TestCase):
    """Юнит-тесты для BaseSCVParser"""

    @parameterized.expand(
        [
            (
                "all_columns_exist",
                ["title", "ctr", "retention_rate"],
                ["title", "ctr", "retention_rate", "views", "likes"],
                True,
            ),
            (
                "missing_one_column",
                ["title", "ctr", "retention_rate"],
                ["title", "retention_rate", "views"],
                False,
            ),
            (
                "missing_multiple_columns",
                ["title", "ctr", "retention_rate"],
                ["title", "views"],
                False,
            ),
            ("empty_header", ["title", "ctr", "retention_rate"], [], False),
            (
                "extra_columns_in_header",
                ["title", "ctr"],
                ["title", "ctr", "retention_rate", "views"],
                True,
            ),
        ]
    )
    def test_check_all_columns_exist(self, name, required_columns, header, expected):
        """Тест проверки наличия всех колонок"""
        parser = BaseSCVParser([], required_columns)
        result = parser._check_all_columns_exist(header, "test_file.csv")
        self.assertEqual(result, expected)

    @parameterized.expand(
        [
            (
                "missing_required_column",
                ["test.csv"],
                ["title", "ctr", "retention_rate"],
                "title,retention_rate\ntitle1,35",  # нет колонки ctr
                0,
            ),
            (
                "missing_multiple_columns",
                ["test.csv"],
                ["title", "ctr", "retention_rate"],
                "title\ntitle1",  # только одна колонка
                0,
            ),
            (
                "wrong_headers",
                ["test.csv"],
                ["title", "ctr", "retention_rate"],
                "name,click,retention\ntitle1,18.2,35",  # другие названия
                0,
            ),
            (
                "empty_header",
                ["test.csv"],
                ["title", "ctr"],
                "\nvalue1,value2",  # пустой заголовок
                0,
            ),
        ]
    )
    @patch("builtins.open")
    def test_get_selected_columns_missing_columns(
        self, name, file_names, columns, csv_content, expected_count, mock_file_open
    ):
        """Тест пропуска файлов с отсутствующими колонками"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value = StringIO(csv_content)
        mock_file_open.return_value = mock_file

        parser = BaseSCVParser(file_names, columns)
        result = parser.get_selected_columns_by_names()

        self.assertEqual(len(result), expected_count)

    @parameterized.expand(
        [
            (
                "mixed_files_one_missing",
                ["valid.csv", "missing.csv"],
                ["title", "ctr"],
                {
                    "valid.csv": "title,ctr\ntitle1,18.2\ntitle2,22.5",
                    "missing.csv": None,  # файл не существует
                },
                2,
            ),  # только valid.csv будет обработан
            (
                "mixed_files_two_valid_one_missing",
                ["valid1.csv", "missing.csv", "valid2.csv"],
                ["title", "ctr"],
                {
                    "valid1.csv": "title,ctr\ntitle1,18.2\ntitle2,22.5",
                    "valid2.csv": "title,ctr\ntitle3,19.0\ntitle4,21.0",
                    "missing.csv": None,
                },
                4,
            ),
        ]
    )
    @patch("builtins.open")
    def test_get_selected_columns_mixed_files(
        self, name, file_names, columns, file_contents, expected_count, mock_file_open
    ):  # noqa
        """Тест обработки смешанных файлов (существующие и нет)"""

        def side_effect(filename, *args, **kwargs):
            if filename in file_contents and file_contents[filename] is not None:
                mock_file = MagicMock()
                mock_file.__enter__.return_value = StringIO(file_contents[filename])
                return mock_file
            else:
                raise FileNotFoundError(f"File {filename} not found")

        mock_file_open.side_effect = side_effect

        parser = BaseSCVParser(file_names, columns)
        result = parser.get_selected_columns_by_names()

        self.assertEqual(len(result), expected_count)

    @patch("csv.reader")
    @patch("builtins.open")
    def test_get_selected_columns_csv_reader_error(
        self, mock_file_open, mock_csv_reader
    ):
        """Тест ошибки CSV reader"""
        mock_file = MagicMock()
        mock_file.__enter__.return_value = StringIO("title,ctr\ntitle1,18.2")
        mock_file_open.return_value = mock_file

        mock_csv_reader.side_effect = csv.Error("CSV parsing error")

        parser = BaseSCVParser(["test.csv"], ["title", "ctr"])

        with patch("csv.reader", side_effect=csv.Error("CSV parsing error")):
            result = parser.get_selected_columns_by_names()
            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
