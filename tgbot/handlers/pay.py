import logging
import pprint

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice

from tgbot.keyboards.inline import payment_ikb
from tgbot.orm.commands import create_order_from_cart, get_order_by_id, clear_user_cart
from tgbot.settings import settings, MIN_PAYMENT_AMOUNT
from tgbot.utils.statesform import StepsFSM
from tgbot.utils.utils import create_xlsx_order, clear_stored_messages
from tgbot.handlers import yookas_pay

logger = logging.getLogger(__name__)


async def send_order(msg: types.Message, bot: Bot, state: FSMContext):
    order = await create_order_from_cart(msg.from_user.id, msg.text)
    if order.summary < MIN_PAYMENT_AMOUNT:
        summary = MIN_PAYMENT_AMOUNT
    else:
        summary = order.summary
    await bot.send_invoice(chat_id=msg.chat.id,
                           title='Оплата заказа',
                           description=f"Количество позиций товаров {len(order.cart)} на общую сумму {order.summary} руб.",
                           payload=f'order_{order.pk}',
                           provider_token=settings.bots.payments,
                           currency='rub',
                           prices=[LabeledPrice(label="Сумма заказа: ", amount=summary*100),
                                   LabeledPrice(label="Скидка: ", amount=-summary*10),
                                   ])


async def pre_checkout_query(precq: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(precq.id, ok=True)


async def success_payment(msg: types.Message, bot: Bot, state: FSMContext):
    order_id = int(msg.successful_payment.invoice_payload.removeprefix("order_"))
    order = await get_order_by_id(order_id)
    logger.info(f'--> Order {order_id} was successfully payed')
    create_xlsx_order(order.cart, order_no=order.pk, date=order.updated, address=order.delivery_address)
    await clear_user_cart(msg.from_user.id)
    await msg.answer(f"Спасибо за покупку на сумму {msg.successful_payment.total_amount // 100} {msg.successful_payment.currency}\n\nЗаявка на доставку сформирована.")
    await clear_stored_messages(bot, msg.chat.id, await state.get_data())
    await state.clear()


async def send_yookassa_order(msg: types.Message, bot: Bot, state: FSMContext):
    order = await create_order_from_cart(msg.from_user.id, msg.text)
    payment_url, payment_id = yookas_pay.create(order.summary, msg.chat.id)
    kbd = payment_ikb(payment_url, payment_id)
    if not await state.set_state():
        await state.set_state(StepsFSM.cart_ordered)
    await state.update_data({'order_id': order.pk})
    await msg.answer(f"Счет {order.pk} на сумму {order.summary} сформирован!", reply_markup=kbd)


async def check_yookassa_handler(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    result = yookas_pay.check(cbk.data.split('_')[-1])
    if result:
        await cbk.message.answer('Оплата прошла успешно!')
        data = await state.get_data()
        order_id = data.get('order_id')
        order = await get_order_by_id(order_id)
        logger.info(f'--> Order {order_id} was successfully payed')
        create_xlsx_order(order.cart, order_no=order.pk, date=order.updated, address=order.delivery_address)
        await clear_user_cart(cbk.message.from_user.id)
        await cbk.message.edit_text(f"Спасибо за покупку на сумму {order.summary} руб.\n\nЗаявка на доставку сформирована.", reply_markup=None)
        await clear_stored_messages(bot, cbk.chat.id, await state.get_data())
        await state.clear()
    else:
        await cbk.message.answer('Оплата еще не прошла или возникла ошибка')
    await cbk.answer()
