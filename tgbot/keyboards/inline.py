import pprint
from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.paginator import Paginator

from tgbot.settings import ITEMS_IN_PAGE, PREF


class CartActions(IntEnum):
    increase = auto()
    decrease = auto()
    cart_add = auto()


class CartCbData(CallbackData, prefix=PREF.cart_add):
    prev_page: int
    item: int
    quantity: int
    action: CartActions


# Не стал создавать CallBack Factory для выбора Групп, Категорий, Товаров и Вопросов, т.к. все они используют
# одну клавиатуру лишь с разными префиксами. Ради этого создавать 4 отдельных класса (т.к. префикс задаётся для класса)
# и 4 одинаковые клавиатуры, различающиеся только использованным внутри классом фабрики, считаю не целесообразным.
def get_catalog_ikb(items: list = None, pref: str = '', page: int = 1, prev=None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    nums1 = []
    if items:
        cur_range = Paginator(items, ITEMS_IN_PAGE).get_page(page)
        for item in cur_range:
            ikb.button(text=item.name, callback_data=f"{pref}_select_{item.pk}")
            nums1.append(1)
        nums2 = 4
        if cur_range.has_previous():
            ikb.button(text="<<", callback_data=f"{pref}_page_{cur_range.previous_page_number()}")
        else:
            nums2 -= 1
        if prev:
            ikb.button(text="Назад", callback_data=prev)
        else:
            nums2 -= 1
        ikb.button(text="🚫 Отменить", callback_data="cancel_soft")
        if cur_range.has_next():
            ikb.button(text=">>", callback_data=f"{pref}_page_{cur_range.next_page_number()}")
        else:
            nums2 -= 1
        ikb.adjust(*nums1, nums2)
    else:
        if prev:
            ikb.button(text="Назад", callback_data=prev)
        ikb.button(text="🚫 Нет записей", callback_data="cancel_soft")
    return ikb.as_markup()


def get_item_ikb(data: CartCbData) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    for label, action in (
            ("+", CartActions.increase),
            ("-", CartActions.decrease),
            ("🛒", CartActions.cart_add),
    ):
        ikb.button(text=label, callback_data=CartCbData(action=action,
                                                        **data.model_dump(include={"prev_page", "item", "quantity"})))
    ikb.adjust(3)
    ikb.button(text="Назад", callback_data=f"{PREF.item}_page_{data.prev_page}")
    ikb.button(text="🚫 Отменить", callback_data="cancel_soft")
    ikb.adjust(2)
    return ikb.as_markup()


def get_cart_ikb(items, pref, page: int = 1) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    nums1 = []
    if items:
        cur_range = Paginator(items, ITEMS_IN_PAGE).get_page(page)
        for item in cur_range:
            ikb.button(text=f"❌ {item.item.name} ({item.qty} шт.)", callback_data=f"{pref}_del_{item.pk}")
            nums1.append(1)
        nums2 = 4
        if cur_range.has_previous():
            ikb.button(text="<<", callback_data=f"{pref}_page_{cur_range.previous_page_number()}")
        else:
            nums2 -= 1
        ikb.button(text="Оформить заказ", callback_data="create_order")
        ikb.button(text="🚫 Закрыть", callback_data="cancel_soft")
        if cur_range.has_next():
            ikb.button(text=">>", callback_data=f"{pref}_page_{cur_range.next_page_number()}")
        else:
            nums2 -= 1
        ikb.adjust(*nums1, nums2)
    else:
        ikb.button(text="🚫 Корзина пуста!", callback_data="cancel_soft")

    return ikb.as_markup()


def payment_ikb(payment_url, payment_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Оплатить',
        url=payment_url
    )
    builder.button(
        text='Проверить оплату',
        callback_data=f'check_{payment_id}'
    )
    return builder.as_markup()


def subscribe_ikb(subscribe_url):
    builder = InlineKeyboardBuilder()
    builder.button(text="Подписаться", url=subscribe_url)
    return builder.as_markup()

