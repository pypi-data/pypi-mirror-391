# nbrb

Python-библиотека для работы с api Национального банка Республики Беларусь (НБ РБ).  

## Возможности

- Получение полного перечня валют, по отношению к которым устанавливается официальный курс белорусского рубля.
- Получение курса конкретной валюты по внутреннему коду НБ РБ, цифровому или буквенном ISO-коду.
- Выборка курсов на произвольную дату и с учётом периодичности (ежедневно/ежемесячно).
- Получение динамики курсов (до 365 дней).
- Поучение ставки рефинсирования.
- Готовый `NBRBClient` с поддержкой переиспользования `requests.Session`, таймаутов и контекстного менеджера.

## Установка

```bash
pip install nbrb
```

## Быстрый старт

```python
from nbrb import fetch_rate

rate = fetch_rate("USD", param_mode=2)
print(f"{rate.cur_scale} {rate.cur_abbreviation}: {rate.cur_official_rate} BYN")
```

## Использование клиента

```python
from datetime import date
from nbrb import NBRBClient

with NBRBClient(timeout=5.0) as client:
    currencies = client.list_currencies()
    usd_today = client.get_rate("USD", param_mode=2)
    usd_history = client.get_rate_dynamics(
        431,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
    )
```

> Больше примеров в файле [examples.py](examples.py)

## Обработка ошибок

Все исключения библиотеки наследуются от `nbrb.NBRBError`.

```python
from nbrb import fetch_rate, HTTPError, NBRBError

try:
    rate = fetch_rate(431)
except HTTPError as exc:
    print(f"API вернуло ошибку: {exc.status_code} - {exc}")
except NBRBError as exc:
    print(f"Произошла ошибка библиотеки: {exc}")
```

## Лицензия

Проект распространяется по лицензии MIT. См. файл [`LICENSE`](LICENSE)


