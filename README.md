# Telegram-bot with Django-admin and ORM 



## Запуск
- скачайте проект
- файл ".env.dist" переименуйте в ".env" и пропишите необходимые настройки
- выполните команды (должен быть запущен Docker):
```bash
# смонтировать контейнер:
docker-compose build
# запустить контейнер:
docker-compose up -d
# остановить контейнер:
docker-compose down
# если в код были внесены изменения, необходимо заново смонтировать контейнер
```


## Миграции
Команды выполняются при запущенном контейнере
```bash
# создание миграций
docker-compose exec web sh -c "python manage.py makemigrations"
# применение миграций
docker-compose exec web sh -c "python manage.py migrate"
# создание суперпользователя
docker-compose exec web sh -c "python manage.py createsuperuser"
```