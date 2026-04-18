import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from typing import List, Optional

from models.YouTube_models import VideoMetrics
from reports.clickbate_reports import clickbait_check
from scv_parser.base_parser import BaseSCVParser


class TestClickbaitCheck(unittest.TestCase):
    """тесты для функции clickbait_check"""

    @parameterized.expand(
        [
            (
                "single_clickbait_video",
                [{"title": "Кликбейт видео 1", "ctr": "25.0", "retention_rate": "22"}],
                1,
                ["Кликбейт видео 1"],
                [25.0],
                [22.0],
            ),
            (
                "multiple_clickbait_videos",
                [
                    {"title": "Видео 1", "ctr": "25.0", "retention_rate": "22"},
                    {"title": "Видео 2", "ctr": "22.5", "retention_rate": "28"},
                    {"title": "Видео 3", "ctr": "18.2", "retention_rate": "35"},
                ],
                3,
                ["Видео 1", "Видео 2", "Видео 3"],
                [25.0, 22.5, 18.2],
                [22.0, 28.0, 35.0],
            ),
            (
                "mixed_clickbait_and_normal",
                [
                    {"title": "Кликбейт 1", "ctr": "25.0", "retention_rate": "22"},
                    {"title": "Нормальное 1", "ctr": "9.5", "retention_rate": "82"},
                    {"title": "Кликбейт 2", "ctr": "19.0", "retention_rate": "38"},
                    {"title": "Нормальное 2", "ctr": "14.2", "retention_rate": "68"},
                ],
                2,  # только 2 кликбейтных
                ["Кликбейт 1", "Кликбейт 2"],
                [25.0, 19.0],
                [22.0, 38.0],
            ),
            (
                "all_clickbait_videos",
                [
                    {"title": "Видео 1", "ctr": "30.0", "retention_rate": "25"},
                    {"title": "Видео 2", "ctr": "28.5", "retention_rate": "30"},
                    {"title": "Видео 3", "ctr": "20.0", "retention_rate": "35"},
                ],
                3,
                ["Видео 1", "Видео 2", "Видео 3"],
                [30.0, 28.5, 20.0],
                [25.0, 30.0, 35.0],
            ),
        ]
    )
    def test_clickbait_check_success(
        self,
        name,
        input_data,
        expected_count,
        expected_titles,
        expected_ctrs,
        expected_retentions,
    ):
        """Тест успешного определения кликбейтных видео"""
        mock_parser = MagicMock(spec=BaseSCVParser)
        mock_parser.get_selected_columns_by_names.return_value = input_data

        result = clickbait_check(mock_parser)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), expected_count)

        for i, video in enumerate(result):
            self.assertIsInstance(video, VideoMetrics)
            self.assertEqual(video.title, expected_titles[i])
            self.assertEqual(video.ctr, expected_ctrs[i])
            self.assertEqual(video.retention_rate, expected_retentions[i])
            self.assertTrue(video.is_clickbait)

    @parameterized.expand(
        [
            ("empty_data", [], 0, []),
            (
                "no_clickbait_videos",
                [
                    {"title": "Нормальное 1", "ctr": "9.5", "retention_rate": "82"},
                    {"title": "Нормальное 2", "ctr": "14.2", "retention_rate": "68"},
                    {"title": "Нормальное 3", "ctr": "16.5", "retention_rate": "42"},
                ],
                0,
                [],
            ),
            (
                "ctr_equal_threshold",
                [{"title": "Граница CTR", "ctr": "15.0", "retention_rate": "35"}],
                0,
                [],
            ),
            (
                "retention_equal_threshold",
                [{"title": "Граница удержания", "ctr": "20.0", "retention_rate": "40"}],
                0,
                [],
            ),
            (
                "ctr_and_retention_on_boundary",
                [{"title": "Обе границы", "ctr": "15.0", "retention_rate": "40"}],
                0,
                [],
            ),
        ]
    )
    def test_clickbait_check_edge_cases(
        self, name, input_data, expected_count, expected_titles
    ):
        """Тест граничных условий"""
        mock_parser = MagicMock(spec=BaseSCVParser)
        mock_parser.get_selected_columns_by_names.return_value = input_data

        result = clickbait_check(mock_parser)

        self.assertEqual(len(result), expected_count)
        if expected_titles:
            for i, video in enumerate(result):
                self.assertEqual(video.title, expected_titles[i])

    @parameterized.expand(
        [
            (
                "missing_title_key",
                [{"ctr": "20.0", "retention_rate": "35"}],  # нет ключа 'title'
                0,
            ),
            (
                "missing_ctr_key",
                [{"title": "Видео", "retention_rate": "35"}],  # нет 'ctr'
                0,
            ),
            (
                "missing_retention_key",
                [{"title": "Видео", "ctr": "20.0"}],  # нет 'retention_rate'
                0,
            ),
            (
                "invalid_ctr_value",
                [{"title": "Видео", "ctr": "not_a_number", "retention_rate": "35"}],
                0,
            ),
            (
                "invalid_retention_value",
                [{"title": "Видео", "ctr": "20.0", "retention_rate": "not_a_number"}],
                0,
            ),
            (
                "empty_string_values",
                [{"title": "", "ctr": "", "retention_rate": ""}],
                0,
            ),
            ("none_values", [{"title": None, "ctr": None, "retention_rate": None}], 0),
        ]
    )
    def test_clickbait_check_error_handling(self, name, input_data, expected_count):
        """Тест обработки ошибочных данных"""
        mock_parser = MagicMock(spec=BaseSCVParser)
        mock_parser.get_selected_columns_by_names.return_value = input_data

        result = clickbait_check(mock_parser)

        self.assertEqual(len(result), expected_count)

    @parameterized.expand(
        [
            (
                "mixed_valid_and_invalid",
                [
                    {"title": "Valid 1", "ctr": "25.0", "retention_rate": "22"},
                    {"title": "Invalid 1", "ctr": "invalid", "retention_rate": "35"},
                    {"title": "Valid 2", "ctr": "20.0", "retention_rate": "30"},
                    {"title": "Invalid 2", "ctr": "18.0", "retention_rate": "bad"},
                ],
                2,
                ["Valid 1", "Valid 2"],
            ),
            (
                "partially_invalid_values",
                [
                    {"title": "Video 1", "ctr": "30.0", "retention_rate": "25"},
                    {"title": "Video 2", "ctr": "25.0", "retention_rate": "invalid"},
                    {"title": "Video 3", "ctr": "invalid", "retention_rate": "30"},
                ],
                1,
                ["Video 1"],
            ),
        ]
    )
    def test_clickbait_check_mixed_valid_invalid(
        self, name, input_data, expected_count, expected_titles
    ):
        """Тест смешанных валидных и невалидных данных"""
        mock_parser = MagicMock(spec=BaseSCVParser)
        mock_parser.get_selected_columns_by_names.return_value = input_data

        result = clickbait_check(mock_parser)

        self.assertEqual(len(result), expected_count)
        for i, video in enumerate(result):
            self.assertEqual(video.title, expected_titles[i])

    def test_clickbait_check_calls_parser_method(self):
        """функция вызывает метод парсера"""
        mock_parser = MagicMock(spec=BaseSCVParser)
        mock_parser.get_selected_columns_by_names.return_value = []

        clickbait_check(mock_parser)

        mock_parser.get_selected_columns_by_names.assert_called_once()

    def test_clickbait_check_returns_list_of_videometrics(self):
        """Тест: функция возвращает список объектов VideoMetrics"""
        input_data = [{"title": "Test", "ctr": "25.0", "retention_rate": "22"}]
        mock_parser = MagicMock(spec=BaseSCVParser)
        mock_parser.get_selected_columns_by_names.return_value = input_data

        result = clickbait_check(mock_parser)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], VideoMetrics)


if __name__ == "__main__":
    unittest.main()
