from __future__ import annotations

__all__ = [
    "NBRBError",
    "HTTPError",
    "InvalidResponseError",
]


class NBRBError(Exception):
    """Базовое исключение для всех ошибок библиотеки."""


class HTTPError(NBRBError):
    """Ошибка HTTP-запроса к API Национального банка."""

    def __init__(self, status_code: int, message: str | None = None) -> None:
        self.status_code = status_code
        self.message = message or f"HTTP {status_code}"
        super().__init__(self.message)


class InvalidResponseError(NBRBError):
    """Ответ API не соответствует ожидаемой структуре."""


