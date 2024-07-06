FROM python:3.11.5

# Установка необходимых пакетов
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения в образ
COPY . .
