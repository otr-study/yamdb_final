![api_yamdb workflow](https://github.com/otr-study/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# API YAMDB
Обеспечивает доступ к API ресурса Yamdb.
Проект YaMDb собирает отзывы пользователей на произведения.

## Стэк технологий:
- Python
- Django Rest Framework
- Postgres
- Docker

## Как запустить проект:

- Склонируйте репозитрий на свой компьютер
- Создайте `.env` файл в директории `infra/`. Пример файла:
    - DB_ENGINE=django.db.backends.postgresql
    - DB_NAME=<имя базы данных>
    - POSTGRES_USER=<Имя пользователя БД>
    - POSTGRES_PASSWORD=<пароль для доступа к БД>
    - DB_HOST=<db>
    - DB_PORT=<5432>
- Из папки `infra/` соберите образ при помощи docker-compose
`$ docker-compose up -d --build`
- Примените миграции
`$ docker-compose exec web python manage.py migrate`
- Соберите статику
`$ docker-compose exec web python manage.py collectstatic --no-input`
- Для доступа к админке не забудьте создать суперюзера
`$ docker-compose exec web python manage.py createsuperuser`
- Для загруки тестовых данных примените команду
`$ docker-compose exec web python manage.py load_data_csv api_yamdb/static/data/`

## Документация API

После установки проекта документация c примерами использования API будет 
доступна по адресу:
```
http://hostname:port/redoc/
```
Где hostname - имя хоста с развернутым проектом, port - номер порта.

## Авторы

[@mkarrr](https://github.com/mkarrr)
[@otr-study](https://github.com/otr-study)
[@odoszhanov](https://github.com/odoszhanov)
