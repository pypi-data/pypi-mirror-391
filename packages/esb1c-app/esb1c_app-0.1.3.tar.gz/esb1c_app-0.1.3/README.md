# esb1c-app

Клиентская библиотека для интеграции с 1C:ESB (1С:Шина), которая помогает получать метаданные каналов, их актуальные назначения и формировать AMQP-подключение для приложений, опубликованных в 1С:Шине.

## Возможности
- `Application` автоматически получает `id_token` по протоколу OAuth 2.0 (`client_credentials`) и переиспользует его во всех запросах.
- Загрузка метаданных каналов (`/sys/esb/metadata/channels`) с разбором описаний и прав доступа.
- Получение актуальных назначений каналов (`/sys/esb/runtime/channels`) и определение активных каналов отправки/получения.
- Формирование AMQP URL вида `amqp://<token>:<token>@<host>:<port>/applications/<application>` на основе данных ESB.

## Установка
```bash
pip install esb1c-app
```

Либо установите из исходников:
```bash
pip install .
```

## Быстрый старт
```python
import os
from esb1c import Application

application = Application(
    url=os.environ["APPLICATION_URL"],
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
)

print(application.id_token)
print(application.sender)
print(application.receiver)
print(application.amqp_url)

print("Исходящие каналы:")
for channel in application.channels.senders:
    print(
        channel.channel,
        channel.process,
        channel.destination,
        channel.channel_description,
        sep=" | ",
    )

print("Входящие каналы:")
for channel in application.channels.receivers:
    print(
        channel.channel,
        channel.process,
        channel.destination,
        channel.process_description,
        sep=" | ",
    )
```

## Переменные окружения
- `APPLICATION_URL` — полный URL вида `http(s)://host(:port)/applications/<имя>` для нужного приложения в 1C:ESB.
- `CLIENT_ID` и `CLIENT_SECRET` — учетные данные пользователя (информационной базы).

Если переменные окружения заданы - библиотека готова к использованию.

## Тестирование
Установите зависимости для разработки:
```bash
pip install .[dev]
```

Запустите тесты:
```bash
pytest
```

По умолчанию запросы к API 1C:ESB подменяются моками. Чтобы прогнать тесты на реальном окружении, задайте переменные `APPLICATION_URL`, `CLIENT_ID`, `CLIENT_SECRET` - это дополнит тестовые наборы (или удалите/отключите фикстуру `mock_requests`).

## Требования
- Python 3.9+
- `requests`

## Лицензия
Проект распространяется по лицензии MIT.

