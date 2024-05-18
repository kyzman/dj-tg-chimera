import asyncio
import logging
import contextlib
import django
import os

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.storage.redis import RedisStorage

from tgbot.settings import settings, WEBHOOK_PATH, WEBHOOK
from tgbot.utils.commands import set_commands
from tgbot.middlewares.security import CheckAllowedMiddleware
from tgbot.handlers import basic

logger = logging.getLogger(__name__)


async def start_bot(bot: Bot):
    await set_commands(bot)


async def stop_bot(bot: Bot):
    ...


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "dj_config.settings"
    )
    os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})
    django.setup()


async def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )
    setup_django()
    bot = Bot(settings.bots.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # storage = RedisStorage.from_url('redis://localhost:6379/0')
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.update.middleware.register(CheckAllowedMiddleware())  # проверка доступа к боту, кому разрешено с ним работать.
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.register(basic.get_start, Command(commands=['start', 'run']))
    dp.message.register(basic.get_help, Command(commands='help'))

    if WEBHOOK:
        app = web.Application()
        webhook_request_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_request_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        return app
    else:
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except Exception as ex:
            logging.error(f"[!!! Exception] - {ex}", exc_info=True)
        finally:
            await bot.session.close()
            await bot.delete_webhook()


if __name__ == '__main__':
    if WEBHOOK:
        web.run_app(start(), host='0.0.0.0', port=8443)
    else:
        with contextlib.suppress(KeyboardInterrupt, SystemExit):
            asyncio.run(start())
