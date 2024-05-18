import logging
import pprint

from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from dj_admin.models import ItemGroup
from django.core.paginator import Paginator

from tgbot.keyboards.inline import get_catalog_ikb
from tgbot.orm.commands import get_groups
from tgbot.utils.statesform import StepsFSM


async def get_catalog(msg: types.Message, bot: Bot, state: FSMContext):
    await state.clear()
    await state.set_state(StepsFSM.select_item)
    await state.set_data({'groups': await get_groups()})
    data = await state.get_data()
    result: list[ItemGroup] = data.get('groups')
    msg_id: types.Message = await msg.answer('Выберете группу товаров:',
                     reply_markup=get_catalog_ikb(result, 'cat'),
                     parse_mode=ParseMode.MARKDOWN)
    await state.update_data({'identity': {'chat_id': msg_id.chat.id, 'msg_id': msg_id.message_id}})


async def msg_cancel_handler(msg: types.Message, bot: Bot, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    data = await state.get_data()
    if ids := data.get('identity'):
        if ids.get('chat_id') == msg.chat.id:
            await bot.edit_message_reply_markup(chat_id=ids.get('chat_id'), message_id=ids.get('msg_id'), reply_markup=None)
        else:
            return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await msg.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def cbk_cancel_handler(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    await cbk.message.edit_reply_markup(reply_markup=None)
    await state.clear()
    await cbk.answer('Cancelled.')


async def get_catalog_page(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    page = int(cbk.data[9:])
    data = await state.get_data()
    result: list[ItemGroup] = data.get('groups')
    ids = data.get('identity')
    await bot.edit_message_reply_markup(chat_id=ids.get('chat_id'), message_id=ids.get('msg_id'),
                                        reply_markup=get_catalog_ikb(result, 'cat', page),
                                        )
    await cbk.answer()

