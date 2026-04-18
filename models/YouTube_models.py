from dataclasses import dataclass
from typing import List


@dataclass
class VideoMetrics:
    """Dataclass для метрик видео"""

    title: str
    ctr: float
    retention_rate: float

    def __post_init__(self):
        """Валидация данных после создания"""
        if not self.title:
            raise ValueError("Название видео не может быть пустым")
        if not 0 <= self.ctr <= 100:
            raise ValueError(f"CTR должен быть между 0 и 100, получено: {self.ctr}")
        if not 0 <= self.retention_rate <= 100:
            raise ValueError(
                f"Retention rate должен быть между 0 и 100, получено: {self.retention_rate}"
            )

    @property
    def is_clickbait(self) -> bool:
        """Проверка на кликбейт"""
        return self.ctr > 15 and self.retention_rate < 40

    @property
    def ctr_formatted(self) -> str:
        "формат с процентами"
        return f"{self.ctr:.1f}%"

    @property
    def retention_formatted(self) -> str:
        "формат с процентами"
        return f"{self.retention_rate:.1f}%"

    def to_table_row(self) -> List[str]:
        """Для отображения в таблице"""
        return [self.title, self.ctr_formatted, self.retention_formatted]


@dataclass
class ReportConfig:
    """Конфигурация отчета"""

    columns: List[str] = None

    def __post_init__(self):
        if self.columns is None:
            self.columns = ["title", "ctr", "retention_rate"]

    @classmethod
    def clickbait_config(cls) -> "ReportConfig":
        """Стандартная конфигурация для кликбейт отчета"""

        return cls(columns=["title", "ctr", "retention_rate"])
