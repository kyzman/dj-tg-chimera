import logging
import pprint
from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware, Bot, types
from aiogram.enums import ChatMemberStatus

from tgbot.keyboards.inline import subscribe_ikb
from tgbot.settings import settings
# from icecream import ic

from tgbot.settings import ALLOWED_IDs, FORBIDDEN_MSG

logger = logging.getLogger(__name__)


def get_allowed(user_id) -> bool:
    if ALLOWED_IDs == '*':
        return True
    else:
        return user_id in ALLOWED_IDs


async def check_subscribe(bot: Bot, chat_id, user_id) -> bool:
    sub = await bot.get_chat_member(chat_id, user_id)
    if sub.status != ChatMemberStatus.LEFT:
        return True
    else:
        return False


class CheckAllowedMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: types.TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        if not await check_subscribe(event.bot, settings.group.id, data['event_from_user'].id):
            await event.bot.send_message(data['event_chat'].id,
                                         'Для работы с ботом необходимо быть подписанным на наш канал',
                                         reply_markup=subscribe_ikb(settings.group.url))
            return

        if get_allowed(data['event_from_user'].id):
            return await handler(event, data)

        try:
            await event.bot.send_message(data['event_chat'].id, FORBIDDEN_MSG)
        except Exception as e:
            logger.error(f"Can't send message: {e}")
