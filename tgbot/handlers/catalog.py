# TODO необходима DRY оптимизация кода
import logging
import pprint

from aiogram import types, Bot, exceptions
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from dj_admin.models import ItemGroup

from tgbot.keyboards.inline import get_catalog_ikb, get_item_ikb, get_cart_ikb, CartCbData, CartActions
from tgbot.orm.commands import get_groups, add_or_update_user, get_category, get_goods_items, get_one_item, add_to_cart, \
    check_in_cart, get_user_cart
from tgbot.settings import PREF, DJANGO_HOST, CART_DESC
from tgbot.utils.statesform import StepsFSM
from tgbot.utils.utils import clear_stored_messages

logger = logging.getLogger(__name__)


async def get_catalog(msg: types.Message, bot: Bot, state: FSMContext):
    logger.info(f'{msg.from_user.id} ({msg.from_user.username}) get catalog request')
    already_msg_id = False
    if await state.get_state() == StepsFSM.select_item:
        data = await state.get_data()
        if not (msg.text == '/cat' or msg.text == '/catalog'):
            await msg.delete()
            return
        else:
            already_msg_id = data.get('identity').get('msg_id')
            await msg.delete()
    else:
        await state.set_state(StepsFSM.select_item)
    data = {'tg_id': int(msg.from_user.id),
            'username': msg.from_user.username,
            'first_name': msg.from_user.first_name,
            'last_name': msg.from_user.last_name}
    await add_or_update_user(data)
    await state.set_state(StepsFSM.select_item)
    await state.update_data({'groups': await get_groups(), 'previous': f"{PREF.group}_page_1"})
    data = await state.get_data()
    result: list[ItemGroup] = data.get('groups')
    image = types.InputMediaPhoto(media='https://boxingmaster.ru/image/cache/katalog-600x315.png', caption='Группа товаров')
    if already_msg_id:
        await bot.edit_message_caption(msg.chat.id, already_msg_id, caption=image.caption, reply_markup=get_catalog_ikb(result, PREF.group, prev=None))
    else:
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

    await clear_stored_messages(bot, msg.chat.id, data)

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await msg.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def cbk_cancel_handler(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    if cbk.message.caption:
        await cbk.message.edit_caption(caption="Вы отменили выбор", reply_markup=None)
    elif cbk.message.text:
        await cbk.message.edit_text(text="Вы отменили выбор", reply_markup=None)
    # await state.clear()
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
    try:
        await cbk.message.edit_media(image,
                                     reply_markup=get_item_ikb(
                                         CartCbData(prev_page=1,
                                                    item=item.pk,
                                                    quantity=1,
                                                    action=CartActions.increase
                                                    )
                                     ))
    except exceptions.TelegramBadRequest as e:
        logger.warning(f"{e}")
        image = types.InputMediaPhoto(media=f"https://www.centervillage.co.jp/images/noimage.png", caption=caption,
                                      parse_mode=ParseMode.HTML)
        await cbk.message.edit_media(image,
                                     reply_markup=get_item_ikb(
                                         CartCbData(prev_page=1,
                                                    item=item.pk,
                                                    quantity=1,
                                                    action=CartActions.increase
                                                    )
                                     ))
        return
    await cbk.answer()


async def manipulate_good_item(cbk: types.CallbackQuery, bot: Bot, state: FSMContext, callback_data: CartCbData):
    caption = cbk.message.caption.splitlines()
    try:
        qty = callback_data.quantity
        qty_text = caption[3]
        summary = caption[4]
    except Exception as e:
        logger.error(f'In callback "{cbk.data}" called by {cbk.from_user.id} ({cbk.from_user.username}): {e}')
        await cbk.answer(f'Ошибка в данных карточки товара: {cbk.data}')
        return
    item = await get_one_item(callback_data.item)  # проверка товара на изменения в базе
    if callback_data.action == CartActions.increase:
        qty += 1
        qty_text = f"Количество: {qty}"
    elif callback_data.action == CartActions.decrease:
        if qty > 1:
            qty -= 1
            qty_text = f"Количество: {qty}"
        else:
            await cbk.answer('Меньше 1 шт добавить нельзя!')
            return
    elif callback_data.action == CartActions.cart_add:
        try:
            _ = caption[6]
            old_qty = (await check_in_cart(cbk.from_user.id, callback_data.item)).qty
        except Exception as e:
            old_qty = 0
        await add_to_cart(cbk.from_user.id, callback_data.item, qty+old_qty)
        await cbk.answer('Добавлено в корзину!')
        st_dta = await state.get_data()
        cart_msg_id = st_dta.get('msg_cart_id')
        if cart_msg_id:
            new_cart = await get_user_cart(cbk.from_user.id)
            cart_msg = f"{CART_DESC}Позиции в корзине <b>({len(new_cart)})</b>:"
            await bot.edit_message_text(cart_msg, chat_id=cbk.message.chat.id, message_id=cart_msg_id, reply_markup=get_cart_ikb(new_cart, PREF.cart_del, -1), parse_mode=ParseMode.HTML)
            await state.update_data({'cart': new_cart})
    caption[3] = qty_text
    caption[0] = f"<b>{caption[0]}</b>"
    price = item.price
    caption[2] = f"Цена: {price}"
    caption[4] = f"<u>Сумма выбранного: {qty*price}</u>"
    new_caption = "\n".join(caption)
    callback_data.quantity = qty
    await cbk.message.edit_caption(caption=new_caption,
                                   reply_markup=get_item_ikb(callback_data),
                                   parse_mode=ParseMode.HTML)
    await cbk.answer()


async def unknown_input(msg: types.Message, bot: Bot):
    await msg.delete()
