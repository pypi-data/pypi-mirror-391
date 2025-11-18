from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable, Mapping, MutableMapping

import requests

from .exceptions import HTTPError, InvalidResponseError, NBRBError
from .models import Currency, Rate, RateShort, RefinancingRate

__all__ = [
    "DEFAULT_BASE_URL",
    "NBRBClient",
    "fetch_currencies",
    "fetch_currency",
    "fetch_rates",
    "fetch_rate",
    "fetch_rate_dynamics",
    "fetch_refinancing_rate",
]

DEFAULT_BASE_URL = "https://api.nbrb.by"


class NBRBClient:
    """HTTP-клиент для API курсов валют Национального банка РБ."""

    def __init__(
        self,
        session: requests.Session | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | tuple[float, float] | None = 10.0,
        user_agent: str | None = None,
    ) -> None:
        self._session = session or requests.Session()
        self._owns_session = session is None
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        if user_agent:
            self._session.headers.setdefault("User-Agent", user_agent)

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

    def __enter__(self) -> "NBRBClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # region public API
    def list_currencies(self) -> list[Currency]:
        """Возвращает полный перечень валют."""
        payload = self._request_json("/exrates/currencies")
        if not isinstance(payload, list):
            raise InvalidResponseError("Ожидался массив валют")
        return [Currency.from_api(item) for item in payload]

    def get_currency(self, cur_id: int) -> Currency:
        """Возвращает информацию о валюте по внутреннему идентификатору."""
        payload = self._request_json(f"/exrates/currencies/{cur_id}")
        if not isinstance(payload, Mapping):
            raise InvalidResponseError("Ожидался объект валюты")
        return Currency.from_api(payload)

    def list_rates(
            self,
            *,
            on_date: _DateLike | None = None,
            periodicity: int = 0,
        ) -> list[Rate]:
        """
        Возвращает курсы валют на указанную дату или текущие.
        
        on_date:     Дата, на которую нужно получить курсы валют (по умолчанию - текущая дата).
        periodicity: Периодичность курса валюты:
            0 – ежедневный (по умолчанию), 
            1 – ежемесячный.
        """
        params: dict[str, Any] = {}
        
        if on_date is not None:
            params["ondate"] = _format_date(on_date)
        params["periodicity"] = periodicity

        payload = self._request_json("/exrates/rates", params=params)
        if not isinstance(payload, list):
            raise InvalidResponseError("Ожидался массив курсов")
        return [Rate.from_api(item) for item in payload]

    def get_rate(
            self,
            cur_id: int | str,
            *,
            on_date: _DateLike | None = None,
            periodicity: int = 0,
            param_mode: int = 0,
        ) -> Rate:
        """
        Возвращает курс конкретной валюты.

        cur_id: Валюта (в зависимости от param_mode).

        on_date:     Дата, на которую нужно получить курсы валют (по умолчанию - текущая дата).
        periodicity: Периодичность курса валюты:
            0 – ежедневный (по умолчанию), 
            1 – ежемесячный.
        param_mode:  Режим параметра `cur_id`: 
            0 – внутренний код валюты (по умолчанию), 
            1 – трехзначный цифровой  код валюты в соответствии со стандартом ИСО 4217, 
            2 – трехзначный буквенный код валюты (ИСО 4217).
        """
        params: dict[str, Any] = {}
        if on_date is not None:
            params["ondate"] = _format_date(on_date)
        params["periodicity"] = periodicity
        params["parammode"] = param_mode
        payload = self._request_json(f"/exrates/rates/{cur_id}", params=params)
        if not isinstance(payload, Mapping):
            raise InvalidResponseError("Ожидался объект курса")
        return Rate.from_api(payload)

    def get_rate_dynamics(
            self,
            cur_id: int,
            *,
            start_date: _DateLike,
            end_date: _DateLike,
        ) -> list[RateShort]:
        
        """Возвращает динамику курса за период (не более 365 дней)."""
        
        params: dict[str, Any] = {
            "startdate": _format_date(start_date),
            "enddate": _format_date(end_date),
        }

        payload = self._request_json(f"/exrates/rates/dynamics/{cur_id}", params=params)
        if not isinstance(payload, list):
            raise InvalidResponseError("Ожидался массив динамики курсов")
        return [RateShort.from_api(item) for item in payload]

    def get_refinancing_rate(
            self,
            *,
            on_date: _DateLike | None = None,
        ) -> RefinancingRate | list[RefinancingRate]:
        """
        Возвращает ставку рефинансирования НБ РБ.
        
        on_date: Дата, на которую запрашивается ставка (необязательный).
                 Если не указана, возвращает массив всех ставок с 1991 года.
        """
        params: dict[str, Any] = {}
        if on_date is not None:
            params["ondate"] = _format_date(on_date)

        payload = self._request_json("/refinancingrate", params=params)
        
        # Расхождение с документацией:
        # API всегда возвращает массив, даже когда указана дата (тогда массив содержит один элемент)
        if not isinstance(payload, list):
            raise InvalidResponseError("Ожидался массив ставок рефинансирования")
        
        if on_date is not None:
            # Если указана дата, возвращается один объект из массива
            if len(payload) == 0:
                raise InvalidResponseError("Не найдена ставка рефинансирования на указанную дату")
            return RefinancingRate.from_api(payload[0])
        else:
            # Если дата не указана, возвращается весь массив
            return [RefinancingRate.from_api(item) for item in payload]

    # endregion

    def _request_json(
            self,
            path: str,
            *,
            params: MutableMapping[str, Any] | None = None,
        ) -> Any:

        url = f"{self._base_url}{path}"
        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
        except requests.RequestException as exc:  # pragma: no cover - сеть нестабильна
            raise NBRBError(f"Не удалось выполнить запрос: {exc}") from exc

        if response.status_code >= 400:
            raise HTTPError(response.status_code, _extract_error_message(response))

        try:
            return response.json()
        except ValueError as exc:
            raise InvalidResponseError("Ответ API не является корректным JSON") from exc


def fetch_currencies(*, client: NBRBClient | None = None) -> list[Currency]:
    
    with _client_context(client) as resolved_client:
        return resolved_client.list_currencies()


def fetch_currency(cur_id: int, *, client: NBRBClient | None = None) -> Currency:
    
    with _client_context(client) as resolved_client:
        return resolved_client.get_currency(cur_id)


def fetch_rates(
        *,
        on_date: _DateLike | None = None,
        periodicity: int = 0,
        client: NBRBClient | None = None,
    ) -> list[Rate]:
    
    with _client_context(client) as resolved_client:
        return resolved_client.list_rates(on_date=on_date, periodicity=periodicity)


def fetch_rate(
        cur_id: int | str,
        *,
        on_date: _DateLike | None = None,
        periodicity: int = 0,
        param_mode: int = 0,
        client: NBRBClient | None = None,
    ) -> Rate:
        
    with _client_context(client) as resolved_client:
        return resolved_client.get_rate(
            cur_id,
            on_date=on_date,
            periodicity=periodicity,
            param_mode=param_mode,
        )


def fetch_rate_dynamics(
        cur_id: int,
        *,
        start_date: _DateLike,
        end_date: _DateLike,
        client: NBRBClient | None = None,
    ) -> list[RateShort]:
    
    with _client_context(client) as resolved_client:
        return resolved_client.get_rate_dynamics(
            cur_id,
            start_date=start_date,
            end_date=end_date,
        )


def fetch_refinancing_rate(
        *,
        on_date: _DateLike | None = None,
        client: NBRBClient | None = None,
    ) -> RefinancingRate | list[RefinancingRate]:
    """
    Возвращает ставку рефинансирования НБ РБ.
    
    on_date: Дата, на которую запрашивается ставка (необязательный).
             Если не указана, возвращает массив всех ставок с 1991 года.
    """
    with _client_context(client) as resolved_client:
        return resolved_client.get_refinancing_rate(on_date=on_date)


def _client_context(client: NBRBClient | None):
    if client is not None:
        return _NullContext(client)
    return NBRBClient()


class _NullContext:
    """Контекстный менеджер-заглушка для использования переданного клиента."""

    def __init__(self, value: NBRBClient) -> None:
        self._value = value

    def __enter__(self) -> NBRBClient:
        return self._value

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - ничего не делаем
        return None


_DateLike = date | datetime | str


def _format_date(value: _DateLike) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    # Этот код ("raise TypeError") никогда не выполнится, потому что предыдущие isinstance проверки покрывают все возможные варианты для _DateLike (str, datetime, date).
    # Можно удалить этот raise или оставить для явного фоллбэка, если типы расширятся. Оставлю с поясняющим комментарием.
    raise TypeError(f"Некорректный тип даты: {type(value)!r}")  # pragma: no cover


def _extract_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or f"HTTP {response.status_code}"

    if isinstance(payload, Mapping):
        for key in ("message", "Message", "error", "Error"):
            if key in payload and isinstance(payload[key], str):
                return payload[key]

    if isinstance(payload, Iterable):
        first = next(iter(payload), None)
        if isinstance(first, Mapping):
            for key in ("message", "Message", "error", "Error"):
                if key in first and isinstance(first[key], str):
                    return first[key]

    return response.text.strip() or f"HTTP {response.status_code}"


