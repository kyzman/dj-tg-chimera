# Telegram-bot with Django-admin and ORM 



## Запуск
- скачайте проект
- файл ".env.dist" переименуйте в ".env" и пропишите необходимые настройки. Так-же необходимо будет настроить settings.py в папке dj_config если вы хотите полноценной работы админки.
- так-же по причине того, что в телеграм нельзя через API загружать картинки с локального компьютера (только уже размещённые в сети) админка Django должна быть настроена и запущена на каком-то хосте с именем и настроенным SSL, поэтому в файле конфигурации бота (tgbot/settings.py) необходимо будет явно указать хост расположения админки django (DJANGO_HOST) чтобы бот мог подгружать оттуда картинки иначе будет отображаться картинка "no image" по умолчанию.
 
- Для создания докер контейнеров выполните команды (должен быть запущен Docker):
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
