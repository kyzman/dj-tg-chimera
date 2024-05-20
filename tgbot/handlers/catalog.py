import logging
import pprint

from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from dj_admin.models import ItemGroup

from tgbot.keyboards.inline import get_catalog_ikb, get_item_ikb
from tgbot.orm.commands import get_groups, add_or_update_user, get_category, get_goods_items, get_one_item, add_to_cart, \
    check_in_cart
from tgbot.settings import PREF, DJANGO_HOST
from tgbot.utils.statesform import StepsFSM

logger = logging.getLogger(__name__)


async def get_catalog(msg: types.Message, bot: Bot, state: FSMContext):
    if await state.get_state():
        await msg.delete()
        return
    data = {'tg_id': int(msg.from_user.id),
            'username': msg.from_user.username,
            'first_name': msg.from_user.first_name,
            'last_name': msg.from_user.last_name}
    await add_or_update_user(data)
    await state.clear()
    await state.set_state(StepsFSM.select_item)
    await state.set_data({'groups': await get_groups(), 'previous': f"{PREF.group}_page_1"})
    data = await state.get_data()
    result: list[ItemGroup] = data.get('groups')
    image = types.InputMediaPhoto(media='https://boxingmaster.ru/image/cache/katalog-600x315.png', caption='Группа товаров')
    msg_id: types.Message = await msg.answer_photo(image.media, image.caption,
                     reply_markup=get_catalog_ikb(result, PREF.group, prev=None),
                     parse_mode=ParseMode.MARKDOWN, allow_sending_without_reply=True)
    await state.update_data({'identity': {'chat_id': msg_id.chat.id, 'msg_id': msg_id.message_id},
                             'photo': types.InputMediaPhoto(media=msg_id.photo[-1].file_id, caption="Группа товаров")})


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
            await bot.edit_message_caption(chat_id=ids.get('chat_id'), message_id=ids.get('msg_id'), caption='Вы отменили выбор', reply_markup=None)
        else:
            return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await msg.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def cbk_cancel_handler(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    await cbk.message.edit_caption(caption="Вы отменили выбор", reply_markup=None)
    await state.clear()
    await cbk.answer('Cancelled.')


async def get_catalog_page(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    page = int(cbk.data.removeprefix(f"{PREF.group}_page_"))
    data = await state.get_data()
    result: list[ItemGroup] = data.get('groups')
    media = data.get('photo')
    await cbk.message.edit_media(media=media, reply_markup=get_catalog_ikb(result, PREF.group, page, prev=None))
    await cbk.answer()


async def get_cat_category(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    group = int(cbk.data.removeprefix(f"{PREF.group}_select_"))
    cat = await get_category(group)
    data = await state.get_data()
    await state.update_data({'category': cat})
    await cbk.message.edit_caption(caption='Выберете категорию товара:', reply_markup=get_catalog_ikb(cat, PREF.category, prev=f"{PREF.group}_page_1"))
    await cbk.answer()


async def get_category_page(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    page = int(cbk.data.removeprefix(f"{PREF.category}_page_"))
    data = await state.get_data()
    result: list[ItemGroup] = data.get('category')
    await cbk.message.edit_reply_markup(reply_markup=get_catalog_ikb(result, PREF.category, page, prev=f"{PREF.group}_page_1"))
    await cbk.answer()


async def select_goods_cat(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    category = int(cbk.data.removeprefix(f"{PREF.category}_select_"))
    items = await get_goods_items(category)
    await state.update_data({'items': items})
    await cbk.message.edit_caption(caption='Выберете товар:', reply_markup=get_catalog_ikb(items, PREF.item, prev=f"{PREF.category}_page_1"))
    await state.update_data({'previous': f"{PREF.category}_page_1"})
    await cbk.answer()


async def get_items_page(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    page = int(cbk.data.removeprefix(f"{PREF.item}_page_"))
    data = await state.get_data()
    result: list[ItemGroup] = data.get('items')
    photo: types.InputMediaPhoto = data.get('photo')
    if photo.media == cbk.message.photo[-1].file_id:
        await cbk.message.edit_reply_markup(reply_markup=get_catalog_ikb(result, PREF.item, page, prev=f"{PREF.category}_page_1"))
    else:
        await cbk.message.edit_media(photo, reply_markup=get_catalog_ikb(result, PREF.item, page, prev=f"{PREF.category}_page_1"))
    await cbk.answer()


async def get_goods_item(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    item_id = int(cbk.data.removeprefix(f"{PREF.item}_select_"))
    item = await get_one_item(item_id)
    in_cart = await check_in_cart(cbk.from_user.id, item)
    caption = f"<b>{item.name}</b>\n{item.desc}\nЦена: {item.price}\nКоличество: 1\nСумма: {item.price}"
    if in_cart:
        caption += f"\n В корзине уже находится {in_cart.qty} шт. на сумму {in_cart.qty*item.price}.\nСколько хотите ещё добавить?"
    image = types.InputMediaPhoto(media=f"{DJANGO_HOST}{item.image.url}", caption=caption, parse_mode=ParseMode.HTML)
    await cbk.message.edit_media(image,
                                 reply_markup=get_item_ikb(item_id,
                                                           {'name': 'К товарам', 'act': f"{PREF.item}_page_1"},
                                                           qty=1,
                                                           pref=PREF.cart_add)
                                 )
    await cbk.answer()


async def manipulate_good_item(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = cbk.data.split(':')
    caption = cbk.message.caption.splitlines()
    try:
        item_id = int(data[1])
        qty = int(data[2])
        operator = data[3]
        qty_text = caption[3]
        summary = caption[4]
    except Exception as e:
        logger.error(f'In callback "{cbk.data}" called by {cbk.from_user.id} ({cbk.from_user.username}): {e}')
        await cbk.answer(f'Ошибка в запросе или данных карточки: {cbk.data}')
        return
    item = await get_one_item(item_id)  # проверка товара на изменения в базе
    if operator == '+':
        qty += 1
        qty_text = f"Количество: {qty}"
    elif operator == '-':
        if qty > 1:
            qty -= 1
            qty_text = f"Количество: {qty}"
        else:
            await cbk.answer('Меньше 1 шт добавить нельзя!')
            return
    elif operator == '=':
        await add_to_cart(cbk.from_user.id, item_id, qty)
        await cbk.answer('Добавлено в корзину!')
        return
    caption[3] = qty_text
    caption[0] = f"<b>{caption[0]}</b>"
    price = item.price
    caption[2] = f"Цена: {price}"
    caption[4] = f"<u>Сумма выбранного: {qty*price}</u>"
    try:
        _ = caption[6]
        old_qty = (await check_in_cart(cbk.from_user.id, item_id)).qty
    except Exception as e:
        old_qty = 0
    new_caption = "\n".join(caption)
    await cbk.message.edit_caption(caption=new_caption,
                                   reply_markup=get_item_ikb(item_id,
                                                           {'name': 'К товарам', 'act': f"{PREF.item}_page_1"},
                                                           qty=qty+old_qty,
                                                           pref=PREF.cart_add),
                                   parse_mode=ParseMode.HTML)
    await cbk.answer()


async def unknown_input(msg: types.Message, bot: Bot):
    await msg.delete()
