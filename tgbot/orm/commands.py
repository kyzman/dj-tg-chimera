# Не оптимизировать импорты и не менять их порядок

import os, django
import pprint

from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_config.settings")
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})
django.setup()

import logging

from asgiref.sync import sync_to_async

from dj_admin.models import TGUser, ItemGroup, ItemCategory, GoodItem, CartItem

logger = logging.getLogger(__name__)


# @sync_to_async
async def add_or_update_user(data: dict) -> TGUser:
    user, created = await TGUser.objects.aupdate_or_create(**data)
    if created:
        logger.info(f"user {user.tg_id} ({user.username}) was added to DB")
    else:
        logger.info(f"User {user.tg_id} ({user.username}) was updated")
    return user


async def get_groups() -> list[ItemGroup]:
    return [group async for group in ItemGroup.objects.all()]


async def get_category(group) -> list[ItemCategory]:
    return [cat async for cat in ItemCategory.objects.filter(group=group)]


async def get_goods_items(category) -> list[GoodItem]:
    return [cat async for cat in GoodItem.objects.filter(cat=category)]


async def get_one_item(item) -> GoodItem | None:
    try:
        obj = await GoodItem.objects.aget(pk=item)
    except ObjectDoesNotExist:
        obj = None
    return obj


async def add_to_cart(tg_user_id, item_id, qty):
    try:
        item = await get_one_item(item_id)
        user = await TGUser.objects.aget(tg_id=tg_user_id)
    except:
        return False
    if await CartItem.objects.filter(user=user, item=item).aupdate(qty=qty):
        ...
    else:
        await CartItem.objects.acreate(user=user, item=item, qty=qty)
    return True


async def check_in_cart(user, item) -> CartItem | None:
    try:
        obj = await CartItem.objects.aget(user=user, item=item)
    except ObjectDoesNotExist:
        obj = None
    return obj
