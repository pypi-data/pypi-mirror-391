# Builder AMQP connection to 1C:ESB application

Библиотека для интеграции с 1C:ESB (1С:Шина), помогающая получать метаданные каналов, их актуальные состояния, направления. Формировать AMQP-подключение к приложениям, опубликованным в 1С:Шине.

## Установка

```bash
pip install esb1c-app
```


## Возможности

- `Application` автоматически получает `id_token` по протоколу OAuth 2.0 (`client_credentials`) и переиспользует его во всех запросах.

- Загрузка метаданных каналов (`/sys/esb/metadata/channels`) с разбором описаний и направлений доступа.

- Получение актуальных назначений каналов (`/sys/esb/runtime/channels`) и определение активных каналов отправки/получения.

- Формирование AMQP URL вида `amqp://<token>:<token>@<host>:<port>/applications/<application>` на основе данных ESB.


## Быстрый старт

see [`example.py`](exapmle.py)

```python
import os
from esb1c import Application

application = Application(
    url=os.environ["APPLICATION_URL"],
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"],
)

print(application.url.to_dict())
```
```json
// json: application.url
{'application_name': 'test',
 'base_url': 'http://srv.dm.local:9090',
 'host': 'src.dm.local',
 'port': 9090,
 'url': 'http://srv.dm.local:9090/applications/test',
 'vhost': '/applications/test'}
```

```python
print("Application sender:")
print(application.sender.to_dict())
```
```json
// json: application sender: 
{
    'access': 'WRITE_ONLY',
    'channel': 'send1',
    'channel_description': 'Источник №1',
    'destination': 'PUBLIC.MDE5YTU1YTZmM...........d3cec70',
    'process': 'my: :test: :Основной: :Дополнительный',
    'process_description': 'Процесс'
}
```
```python
print("Application receiver:")
print(application.receiver.to_dict())
```
```json
// jsom: application receiver: 
{
    'access': 'READ_ONLY',
    'channel': 'rec1',
    'channel_description': 'Получатель №1',
    'destination': 'PUBLIC.MDE5YTU1YTZmM............d3cec70',
    'process': 'my: :test: :Основной: :Дополнительный',
    'process_description': 'Процесс'
}
```
```python

# token авторизации
print(application.id_token)

# каналы отправитель и получатель
print(application.sender)
print(application.receiver)

# строка соединения по протоколу amqp с токенами
print(application.amqp_url)

# Исходящие каналы
for channel in application.channels.senders:
    print(
        channel.channel,
        channel.process,
        channel.destination,
        channel.channel_description,
    )

# Входящие каналы
for channel in application.channels.receivers:
    print(
        channel.channel,
        channel.process,
        channel.destination,
        channel.process_description,
    )
```

## Переменные окружения
- `APPLICATION_URL` — полный URL приложения в 1C:ESB вида `http(s)://host(:port)/applications/<имя>`.
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
