from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.paginator import Paginator

from tgbot.settings import ITEMS_IN_PAGE


def get_catalog_ikb(items: list = None, pref: str = '', page: int = 1) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    nums1 = []
    if items:
        cur_range = Paginator(items, ITEMS_IN_PAGE).get_page(page)
        for item in cur_range:
            ikb.button(text=item.name, callback_data=f"{pref}_{item.pk}")
            nums1.append(1)
        nums2 = 3
        if cur_range.has_previous():
            ikb.button(text="<<", callback_data=f"{pref}_page_{cur_range.previous_page_number()}")
        else:
            nums2 -= 1
        ikb.button(text="🚫 Отменить", callback_data="cancel_soft")
        if cur_range.has_next():
            ikb.button(text=">>", callback_data=f"{pref}_page_{cur_range.next_page_number()}")
        else:
            nums2 -= 1
        ikb.adjust(*nums1, nums2)
    else:
        ikb.button(text="🚫 Нет записей", callback_data="cancel_soft")
    return ikb.as_markup()
