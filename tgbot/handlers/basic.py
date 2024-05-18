import pprint

from aiogram import Bot, types

from tgbot.orm.commands import add_or_update_user
from tgbot.settings import BASE_HELP


async def get_start(msg: types.Message, bot: Bot):
    data = {'tg_id': int(msg.from_user.id),
            'username': msg.from_user.username,
            'first_name': msg.from_user.first_name,
            'last_name': msg.from_user.last_name}
    user = await add_or_update_user(data)
    await msg.answer(f'Привет. Вы в базе с id {user.tg_id}')
    await bot.send_message(msg.from_user.id, f"<b>Привет {msg.from_user.first_name}. Рад тебя видеть!</b>")


async def get_help(msg: types.Message, bot: Bot):
    await bot.send_message(msg.from_user.id, BASE_HELP, parse_mode='HTML')
