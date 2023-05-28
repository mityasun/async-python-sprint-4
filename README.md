## Описание проекта 
#### Сервис для сокращения ссылок.

### Возможности проекта:
- Получение статуса подключения к базе данных.
- Создание сокращенной ссылки из оригинальной.
- Групповое создание сокращенных ссылок из оригинальных.
- Получение оригинальной ссылки по id сокращенной.
- Получение статуса количества раз использования сокращенной ссылки.
- Получение полного статуса использования сокращенной ссылки: список клиентов, которые ее использовали и дата использования.
- Удаление сокращенной ссылки (в БД ссылка не удаляется, а устанавливается соответствующий статус) 
- Блокировка доступа к сервису по IP.

### Как запустить проект локально с помощью Doker:

Клонировать репозиторий и перейти в него в терминале:

```
git clone https://github.com/mityasun/async-python-sprint-4.git
```

Перейдите в директорию с настройками Docker-compose:

```
cd async-python-sprint-4
```

Создайте в этой директории файл .env на основе файла-примера env.docker.example:

```
APP_TITLE='Link shortening service'
PROJECT_HOST=127.0.0.1
PROJECT_PORT=8000
DATABASE_DSN=postgresql+asyncpg://postgres:postgres@url_postgres:5432/postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

Запустите сборку образа и запуск сервиса из файла Docker-compose:
```
docker-compose up -d --build
```

Спецификация API будет доступна по ссылке:
```
http://127.0.0.1:8000/redoc
```



# Проектное задание четвёртого спринта

Спроектируйте и реализуйте сервис для создания сокращённой формы передаваемых URL и анализа активности их использования.

Кроме этого, выберите из списка дополнительные требования и тоже реализуйте их. У каждого задания есть определённая сложность, от которой зависит количество баллов. Вам необходимо выбрать такое количество заданий, чтобы общая сумма баллов была больше 4. Выбор заданий никак не ограничен: можно выбрать все простые или одно среднее и два простых, или одно продвинутое, или решить все.

## Описание задания

Реализовать `http`-сервис, который обрабатывает поступающие запросы. Сервер стартует по адресу `http://127.0.0.1:8080` (значение по умолчанию, можно изменять).

<details>
<summary> Список возможных эндпойнтов (можно изменять) </summary>

1. Получить сокращённый вариант переданного URL.

```python
POST /
```

Метод принимает в теле запроса строку URL для сокращения и возвращает ответ с кодом `201`.

2. Вернуть оригинальный URL.

```python
GET /<shorten-url-id>
```

Метод принимает в качестве параметра идентификатор сокращённого URL и возвращает ответ с кодом `307` и оригинальным URL в заголовке `Location`.

3. Вернуть статус использования URL.

```python
GET /<shorten-url-id>/status?[full-info]&[max-result=10]&[offset=0]
```

Метод принимает в качестве параметра идентификатор сокращённого URL и возвращает информацию о количестве переходов, совершенных по ссылке.

В ответе может содержаться как общее количество совершенных переходов, так и дополнительная детализированная информация о каждом переходе (наличие **query**-параметра **full-info** и параметров пагинации):
- дата и время перехода/использования ссылки;
- информация о клиенте, выполнившем запрос;

</details>


## Дополнительные требования (отметьте [Х] выбранные пункты):

- [x] (1 балл) Реализуйте метод `GET /ping`, который возвращает информацию о статусе доступности БД.
- [x] (1 балл) Реализуйте возможность «удаления» сохранённого URL. Запись должна остаться, но помечаться как удалённая. При попытке получения полного URL возвращать ответ с кодом `410 Gone`.
- [x] (2 балла) Реализуйте middlware, блокирующий доступ к сервису из запрещённых подсетей (black list).
- [x] (2 балла) Реализуйте возможность передавать ссылки пачками (batch upload).

<details>
<summary> Описание изменений </summary>

- Метод `POST /shorten` принимает в теле запроса список URL в формате:

```python
[
    {
        "original-url": "<URL-for-shorten>"
    },
    ...
]

```
... и возвращает данные в следующем формате:

```python
[
    {
        "short-id": "<shoten-id>",
        "short-url": "http://...",
    },
    ...
]
```
</details>


- [ ] (3 балла) Реализуйте взаимодействие с сервисом авторизованного пользователя. Пользователь может создавать как приватные, так и публичные ссылки или изменять видимость ссылок. Вызов метода `GET /user/status` возвращает все созданные ранее ссылки в формате:

```
[
    {
        "short-id": "<text-id>",
        "short-url": "http://...",
        "original-url": "http://...",
        "type": "<public|private>"
    },
    ...
]
```

- [ ] **(5 баллов) Реализуйте кастомное взаимодействия с БД. Необходимо учесть возможность работы с транзакциями.


## Требования к решению

1. Используйте фреймворк FastAPI. В качестве СУБД используйте PostgreSQL (не ниже 10 версии).
2. Используйте концепции ООП.
3. Предусмотрите обработку исключительных ситуаций.
4. Приведите стиль кода в соответствие pep8, flake8, mypy.
5. Логируйте результаты действий.
6. Покройте написанный код тестами.
