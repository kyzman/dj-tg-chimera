from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
# from icecream import ic

from tgbot.settings import ALLOWED_IDs, FORBIDDEN_MSG


def get_allowed(user_id) -> bool:
    if ALLOWED_IDs == '*':
        return True
    else:
        return user_id in ALLOWED_IDs


class CheckAllowedMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        if get_allowed(data['event_from_user'].id):
            return await handler(event, data)
        try:
            await event.bot.send_message(data['event_chat'].id, FORBIDDEN_MSG)
        except:
            print('Не удалось идентифицировать чат события')
