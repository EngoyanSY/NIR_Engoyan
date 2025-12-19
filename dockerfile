FROM python:3.11-slim

# Устанавливаем необходимые системные зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем всё в /app
COPY . /app

WORKDIR /app/server

# Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

# Запуск: миграции → статика → gunicorn
CMD ["sh", "-c", "python manage.py migrate && \
                     python manage.py collectstatic --noinput && \
                     python manage.py loaddata /app/db_dump.json && \
                     gunicorn nir.wsgi:application --bind 0.0.0.0:8000"]