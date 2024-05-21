import pprint

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.paginator import Paginator

from tgbot.settings import ITEMS_IN_PAGE


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


def get_item_ikb(item, prev=None, qty: int = 1, pref: str = 'add') -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text="+", callback_data=f"{pref}:{item}:{qty}:+")
    ikb.button(text="-", callback_data=f"{pref}:{item}:{qty}:-")
    ikb.button(text="🛒 В корзину", callback_data=f"{pref}:{item}:{qty}:=")
    ikb.adjust(3)
    if prev:
        ikb.button(text=prev.get('name', 'Назад'), callback_data=prev.get('act', 'unk'))
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

