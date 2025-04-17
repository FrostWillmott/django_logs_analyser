from typing import Type, Dict
from .base import Report

registry: Dict[str, Type[Report]] = {}


def register_report(cls: Type[Report]) -> Type[Report]:
    """
    Декоратор для регистрации отчётов в реестре.
    """
    if not hasattr(cls, "name"):
        raise ValueError("Report class must have a 'name' attribute")
    registry[cls.name] = cls
    return cls


# Регистрируем все отчёты при импорте
from . import handlers  # noqa: F401
