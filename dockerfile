FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Собираем статические файлы
# RUN python server/manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python server/manage.py migrate && python server/manage.py collectstatic --noinput && gunicorn nir.wsgi:application --bind 0.0.0.0:8000"]