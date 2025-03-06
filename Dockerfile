# Dockerfile:

# Базовый образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем requirements.txt из корня проекта
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем папку backend с Django-приложением
COPY backend /app/

# Открываем порт для внешнего доступа
EXPOSE 8000

# Запускаем Django-сервер
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
