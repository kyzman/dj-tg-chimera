import logging
import pprint

from aiogram import Bot, types
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext

from tgbot.orm.commands import add_or_update_user
from tgbot.settings import BASE_HELP

logger = logging.getLogger(__name__)


async def get_start(msg: types.Message, bot: Bot, state: FSMContext):
    if await state.get_state():
        await msg.delete()
        return
    data = {'tg_id': int(msg.from_user.id),
            'username': msg.from_user.username,
            'first_name': msg.from_user.first_name,
            'last_name': msg.from_user.last_name}
    user = await add_or_update_user(data)
    await msg.answer(f'Привет. Вы в базе с id {user.tg_id}')
    await bot.send_message(msg.from_user.id, f"<b>Привет {msg.from_user.first_name}. Рад тебя видеть!</b>")


async def get_help(msg: types.Message, bot: Bot):
    await bot.send_message(msg.from_user.id, BASE_HELP, parse_mode='HTML')


async def unknown_command(msg: types.Message, bot: Bot):
    if msg.chat.type == ChatType.PRIVATE:
        await msg.answer(f'Привет {msg.from_user.first_name}.\nДля помощи введите /help\nДля регистрации(обновления) сведений введите /start\n'
                     'Внимание! Взаимодействуя с этим ботом(при отправке команд, кроме /help) вы соглашаетесь на обработку персональных данных.')


async def unknown_callback(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    logger.warning(f'User {cbk.from_user.id} ({cbk.from_user.username}) try to call "{cbk.data}" without state')
    if cbk.message.text:
        await cbk.message.edit_text('Сообщение потеряло актуальность из-за внутреннего сбоя, пожалуйста начните снова.', reply_markup=None)
    elif cbk.message.caption:
        await cbk.message.edit_caption(caption='Сообщение потеряло актуальность из-за внутреннего сбоя, пожалуйста начните снова.',
                                    reply_markup=None)
    await cbk.answer('Ошибка!')
