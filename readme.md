Версия python - 3.9

## Установка виртуального окружения
```
python -m venv venv
```
## Активация виртуального оуркжения
```
source venv/bin/activate  # linux
```
```
venv\Scripts\activate  # windows
```
## Установка зависимостей
```
python -m pip install --upgrade pip
```
Установка:
```
pip install -r .\requirements.txt
```

## Запуск сервера
```
python server/manage.py runserver
```

## Дамп
```
python server/manage.py dumpdata > db_dump.json
python server/manage.py dump_utf8 --output=correct_dump.json
```

## Докер
```
docker-compose up --build
docker-compose exec web python server/manage.py loaddata /app/db_dump.json
```

## Включение сервера
```
ssh -R 80:localhost:8000 serveo.net
```