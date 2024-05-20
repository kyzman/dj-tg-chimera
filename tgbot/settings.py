from environs import Env
from dataclasses import dataclass

BASE_HELP = '''/start - начать работу, зарегистрироваться в системе или обновить информацию.
/help получить эту помощь
/stop, /cancel, /restart - отменить все действия и вернуться к изначальному состоянию.
/cat, /catalog - посмотреть каталог товаров.
'''

FORBIDDEN_MSG = "Вам запрещено взаимодействие с этим ботом!"

# правила безопасности работы с ботом ('*' для доступа всем)
ALLOWED_IDs = '*'
# {5027774009,}
# Список telegram ID пользователей, кому будет разрешено взаимодействие с ботом

ITEMS_IN_PAGE = 3

# хост где будет расположен проект DJANGO. Необходимо для корректной загрузки изображений.
DJANGO_HOST = 'https://kyzman.pythonanywhere.com'  # временно указан тестовый

@dataclass
class PREF:
    group = 'grp'
    category = 'cat'
    item = 'itm'
    cart_add = 'add'  # Don't use ':' in that field!


@dataclass
class Bots:
    bot_token: str
    admin_id: int


@dataclass
class Db:
    host: str
    database: str
    user: str
    password: str
    users_table: str


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            admin_id=env.int("ADMIN_ID"),
        ),
    )


settings = get_settings('.env')

WEBHOOK = False
WEBHOOK_HOST = ''  # Путь к серверу где будет обрабатываться webhook
WEBHOOK_PATH = f"/{settings.bots.bot_token}"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}"

# file '.env' must be in root folder and have text format such as:
# TOKEN=your bot token
# ADMIN_ID=your telegram ID
