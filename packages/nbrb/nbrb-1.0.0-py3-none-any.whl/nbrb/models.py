from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping

__all__ = [
    "Currency",
    "Rate",
    "RateShort",
    "RefinancingRate",
]


def _parse_date(value: str) -> "Date":
    """Преобразует строку даты из API в `date`."""
    try:
        # API возвращает даты в формате YYYY-MM-DD[T]HH:MM:SS
        return Date(datetime.fromisoformat(value).date())
    except ValueError as exc:  # pragma: no cover - защищаемся от неожиданных форматов
        raise ValueError(f"Некорректный формат даты: {value!r}") from exc


def _parse_decimal(value: Any, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (ArithmeticError, ValueError, TypeError) as exc:
        raise ValueError(f"Некорректное числовое значение {field_name}: {value!r}") from exc

class Date(date):
    """Поле даты с кастомным представлением."""
    
    def __new__(cls, year: int | date, month: int | None = None, day: int | None = None) -> "Date":
        """Создаёт объект Date из date или из year/month/day."""
        if isinstance(year, date):
            # Если передан объект date, извлекаем его компоненты
            return super().__new__(cls, year.year, year.month, year.day)
        # Иначе используем стандартный конструктор date(year, month, day)
        if month is None or day is None:
            raise TypeError("Date требует либо date объект, либо (year, month, day)")
        return super().__new__(cls, year, month, day)
    
    def __repr__(self) -> str:
        return f"Date({self})"
    
    def __str__(self) -> str:
        return self.strftime("%d.%m.%Y")

@dataclass(frozen=True, slots=True)
class Currency:
    """Описание валюты, используемой Национальным банком Республики Беларусь."""

    cur_id: int
    cur_parent_id: int | None
    cur_code: int | None
    cur_abbreviation: str
    cur_name: str
    cur_name_bel: str | None
    cur_name_eng: str | None
    cur_quot_name: str | None
    cur_quot_name_bel: str | None
    cur_quot_name_eng: str | None
    cur_name_multi: str | None
    cur_name_bel_multi: str | None
    cur_name_eng_multi: str | None
    cur_scale: int
    cur_periodicity: int
    cur_date_start: date
    cur_date_end: date | None

    def __repr__(self) -> str:
        period = f"from {self.cur_date_start.year} to {self.cur_date_end.year}" if self.cur_date_end and self.cur_date_end < date.today() else None
        period_view = f", period: {period}" if period else ""
        return f"Currency(id={self.cur_id}, {self.cur_abbreviation}, {self.cur_name}{period_view})"
    
    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "Currency":
        """Создаёт объект `Currency` из ответа API."""
        return cls(
            cur_id=int(payload["Cur_ID"]),
            cur_parent_id=_optional_int(payload.get("Cur_ParentID")),
            cur_code=_optional_int(payload.get("Cur_Code")),
            cur_abbreviation=str(payload["Cur_Abbreviation"]),
            cur_name=str(payload["Cur_Name"]),
            cur_name_bel=_optional_str(payload.get("Cur_Name_Bel")),
            cur_name_eng=_optional_str(payload.get("Cur_Name_Eng")),
            cur_quot_name=_optional_str(payload.get("Cur_QuotName")),
            cur_quot_name_bel=_optional_str(payload.get("Cur_QuotName_Bel")),
            cur_quot_name_eng=_optional_str(payload.get("Cur_QuotName_Eng")),
            cur_name_multi=_optional_str(payload.get("Cur_NameMulti")),
            cur_name_bel_multi=_optional_str(payload.get("Cur_Name_BelMulti")),
            cur_name_eng_multi=_optional_str(payload.get("Cur_Name_EngMulti")),
            cur_scale=int(payload["Cur_Scale"]),
            cur_periodicity=int(payload["Cur_Periodicity"]),
            cur_date_start=_parse_date(str(payload["Cur_DateStart"])),
            cur_date_end=_optional_date(payload.get("Cur_DateEnd")),
        )


@dataclass(frozen=True, slots=True)
class Rate:
    """Официальный курс белорусского рубля к иностранной валюте."""

    cur_id: int
    date: date
    cur_abbreviation: str
    cur_scale: int
    cur_name: str
    cur_official_rate: Decimal

    def __repr__(self) -> str:
        return f"Rate({self.cur_scale} {self.cur_abbreviation}={self.cur_official_rate} on {self.date}, {self.cur_name})"

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "Rate":
        return cls(
            cur_id=int(payload["Cur_ID"]),
            date=_parse_date(str(payload["Date"])),
            cur_abbreviation=str(payload["Cur_Abbreviation"]),
            cur_scale=int(payload["Cur_Scale"]),
            cur_name=str(payload["Cur_Name"]),
            cur_official_rate=_parse_decimal(payload["Cur_OfficialRate"], "Cur_OfficialRate"),
        )


@dataclass(frozen=True, slots=True)
class RateShort:
    """Упрощённое представление курса для динамики."""

    cur_id: int
    date: date
    cur_official_rate: Decimal

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "RateShort":
        return cls(
            cur_id=int(payload["Cur_ID"]),
            date=_parse_date(str(payload["Date"])),
            cur_official_rate=_parse_decimal(payload["Cur_OfficialRate"], "Cur_OfficialRate"),
        )


@dataclass(frozen=True, slots=True)
class RefinancingRate:
    """Ставка рефинансирования Национального банка Республики Беларусь."""

    date: date
    value: Decimal

    def __repr__(self) -> str:
        return f"RefinancingRate({self.value}% on {self.date})"

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "RefinancingRate":
        """Создаёт объект `RefinancingRate` из ответа API."""
        return cls(
            date=_parse_date(str(payload["Date"])),
            value=_parse_decimal(payload["Value"], "Value"),
        )


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _optional_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    return _parse_date(str(value))


