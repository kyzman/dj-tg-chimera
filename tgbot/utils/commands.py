from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='stop',
            description='Отменить (начать сначала)'
        ),
        BotCommand(
            command='help',
            description='Помощь'
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
