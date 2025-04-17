from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

T = TypeVar("T")


class Report(ABC, Generic[T]):
    """
    Базовый класс для отчетов.
    Каждый отчет должен задавать атрибут name
    и реализовывать методы process_file, combine, render.
    """

    name: str

    @abstractmethod
    def process_file(self, path: str) -> T:
        """
        Обработка одного файла лога.
        Возвращает промежуточные данные типа T.
        """
        ...

    @abstractmethod
    def combine(self, results: List[T]) -> T:
        """
        Объединяет промежуточные данные из нескольких файлов.
        """
        ...

    @abstractmethod
    def render(self, data: T) -> str:
        """
        Формирует строковое представление отчёта.
        """
        ...
