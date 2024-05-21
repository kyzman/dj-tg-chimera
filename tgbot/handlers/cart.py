import pprint

from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from dj_admin.models import CartItem
from tgbot.keyboards.inline import get_cart_ikb
from tgbot.orm.commands import get_user_cart, del_item_from_cart
from tgbot.settings import PREF, CART_DESC
from tgbot.utils.statesform import StepsFSM
from tgbot.utils.utils import check_cart_actuality


async def get_cart(msg: types.Message, bot: Bot, state: FSMContext):
    if not await state.get_state():
        await state.set_state(StepsFSM.item_selected)
    cart_items = await get_user_cart(msg.from_user.id)
    await state.update_data({'cart': cart_items})
    msg_id: types.Message = await msg.answer(f'{CART_DESC}Позиции в корзине ({len(cart_items)}):',
                                             reply_markup=get_cart_ikb(cart_items, PREF.cart_del), parse_mode=ParseMode.HTML)
    await state.update_data({'msg_cart_id': msg_id.message_id})


async def get_cart_page(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    if not await check_cart_actuality(cbk.message, state):
        await cbk.answer('Данная корзина потеряла актуальность!')
        return
    page = int(cbk.data.removeprefix(f"{PREF.cart_del}_page_"))
    data = await state.get_data()
    result: list[CartItem] = data.get('cart')
    await cbk.message.edit_reply_markup(reply_markup=get_cart_ikb(result, PREF.cart_del, page=page))
    await cbk.answer()


async def del_cart_item(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    if not await check_cart_actuality(cbk.message, state):
        await cbk.answer('Данная корзина потеряла актуальность!')
        return
    item_id = int(cbk.data.removeprefix(f"{PREF.cart_del}_del_"))
    if await del_item_from_cart(item_id):
        await cbk.answer('Товар удалён из корзины!')
        upd_cart = await get_user_cart(cbk.from_user.id)
        await state.update_data({'cart': upd_cart})
        await cbk.message.edit_text(f"{CART_DESC}Позиции в корзине <b>({len(upd_cart)})</b>:", reply_markup=get_cart_ikb(upd_cart, PREF.cart_del, -1), parse_mode=ParseMode.HTML)
    else:
        await cbk.answer('Ошибка при удалении товара!')


async def input_address(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    if not await check_cart_actuality(cbk.message, state):
        await cbk.answer('Данная корзина потеряла актуальность!\n Откройте новую!')
        return
    await cbk.message.answer('Введите адрес для доставки товара:')
    await state.set_state(StepsFSM.cart_order)
    await cbk.answer()

#
# async def create_order(msg: types.Message, bot: Bot, state: FSMContext):
#     await create_order_from_cart(msg.from_user.id, msg.text)
#     await clear_user_cart(msg.from_user.id)
#     await msg.answer(f'Заказ на адрес {msg.text} создан!')
#     await clear_stored_messages(bot, msg.chat.id, await state.get_data())
#     await state.clear()
