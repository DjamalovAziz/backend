# Dockerfile:

FROM python:3.13-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Копируем папку backend с Django-приложением
COPY backend /app/

# Открываем порт для внешнего доступа
EXPOSE 8000

# Запускаем Django-сервер
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
