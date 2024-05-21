import logging
import pprint

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice

from tgbot.orm.commands import create_order_from_cart, get_order_by_id, clear_user_cart
from tgbot.settings import settings, MIN_PAYMENT_AMOUNT
from tgbot.utils.utils import create_xlsx_order, clear_stored_messages

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
