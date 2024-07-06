# Docker Контейнер для Python приложения с PostgreSQL

Этот репозиторий содержит файлы для создания Docker контейнера, который запускает Python приложение с PostgreSQL базой данных.

## Структура проекта

- `Dockerfile`: Определяет, как собрать Docker образ.
- `docker-compose.yml`: Определяет конфигурацию Docker Compose для запуска приложения и базы данных.
- `requirements.txt`: Список Python пакетов, необходимых для приложения.

## Шаги для сборки и запуска

### 1. Установка Docker

Если у вас еще нет Docker на вашем компьютере, скачайте и установите его с [официального сайта Docker](https://www.docker.com/).

### 2. Сборка Docker образа

Выполните следующие команды для сборки Docker образа:

```bash
docker build -t test_task .
```


### 3. Запуск Docker контейнера

Используйте docker-compose для запуска контейнера с приложением и базой данных PostgreSQL. Создайте файл docker-compose.yml со следующим содержимым:

```yaml
version: '3.11'

services:
  web:
    build: .
    command: bash -c 'while !</dev/tcp/db/5432; do sleep 1; done; uvicorn app.main:app --host 0.0.0.0 --reload'
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/base
    depends_on:
      - db

  db:
    image: postgis/postgis:15-3.4
    restart: on-failure
    volumes:
      - postgres_data:/var/lib/postgresql/data
    expose:
      - "5432"
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=passwor
      - POSTGRES_DB=base

volumes:
  postgres_data:
```

В `environment:` используйте свои данные для подключения к базе `PostgreSQL`

### Запуск контейнера через Docker Compose
Выполните следующую команду в директории с вашим `docker-compose.yml` файлом:

```bash
docker-compose up
```

Эта команда запустит два сервиса: `web` (ваше Python приложение) и `db` (PostgreSQL база данных с расширеннием PostGIS). Приложение будет доступно на `http://localhost:8000`.

### Примечание

 - Если вам нужно изменить зависимости Python приложения (`requirements.txt`), обновите этот файл и пересоберите Docker образ с помощью `docker build`.
 - При первом запуске базы данных PostgreSQL, возможно потребуется некоторое время для инициализации.

