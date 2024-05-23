from environs import Env
from dataclasses import dataclass
from openpyxl.styles import Side

BASE_HELP = '''/start - начать работу, зарегистрироваться в системе или обновить информацию.
/help получить эту помощь
/stop, /cancel, /restart - жёстко отменить все действия и вернуться к изначальному состоянию.
/cat, /catalog - посмотреть каталог товаров.
/cart - посмотреть корзину (работает и во время выбора товаров)
/faq - посмотреть список часто задаваемых вопросов и/или задать свой.
'''

double = Side(border_style="medium", color="00000000")
thin = Side(border_style="thin", color="00000000")

MIN_PAYMENT_AMOUNT = 111

CART_DESC = "Список выбранных товаров к заказу.\nВыберете позицию из списка для удаления.\n"

FORBIDDEN_MSG = "Вам запрещено взаимодействие с этим ботом!"

# Используется для ограничения доступа работы с ботом ('*' для доступа всем)
# Список telegram ID пользователей, кому будет разрешено взаимодействие с ботом - '*' - нет ограничений.
ALLOWED_IDs = '*'

ITEMS_IN_PAGE = 3

# хост где будет расположен проект DJANGO. Необходимо для корректной загрузки изображений в бота.
DJANGO_HOST = 'https://kyzman.pythonanywhere.com'  # временно указан тестовый


@dataclass
class PREF:
    group = 'grp'
    category = 'cat'
    item = 'itm'
    cart_add = 'add'  # Don't use ':' in that field!
    cart_del = 'del'
    question = 'qst'


@dataclass
class Bots:
    bot_token: str
    admin_id: int
    payments: str


@dataclass
class Yookassa:
    account: str
    secret: str


@dataclass
class Group:
    id: int
    url: str


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
    yookassa: Yookassa
    group: Group


def get_settings(path: str):
    env = Env()
    env.read_env(path)
    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            admin_id=env.int("ADMIN_ID"),
            payments=env.str("PAYMENTS"),
            ),
        yookassa=Yookassa(
            account=env.str("ACCOUNT_ID"),
            secret=env.str("SECRET_KEY")
            ),
        group=Group(id=env.int("BOT_GROUP"),
                    url=env.str("BOT_GROUP_URL"))
    )


settings = get_settings('.env')

WEBHOOK = False
WEBHOOK_HOST = ''  # Путь к серверу где будет обрабатываться webhook
WEBHOOK_PATH = f"/{settings.bots.bot_token}"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}"

# file '.env' must be in root folder and have text format such as:
# TOKEN=your bot token
# ADMIN_ID=your telegram ID
