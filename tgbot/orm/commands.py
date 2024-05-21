# TODO использование orm django плохая идея, т.к. возникает проблема конечности пула соединений. Для частичного решения можно использовать pgBouncer, но лучшее решение отказаться от orm django и использовать асинхронную sqlalchemy
# Не оптимизировать импорты и не менять их порядок

import os, django
import pprint

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_config.settings")
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})
django.setup()

import logging

from asgiref.sync import sync_to_async

from dj_admin.models import TGUser, ItemGroup, ItemCategory, GoodItem, CartItem, Order, Question

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


async def get_user_cart(user) -> list[CartItem]:
    return [item async for item in CartItem.objects.filter(user=user)]


async def del_item_from_cart(rec_id):
    try:
        b = await CartItem.objects.aget(pk=rec_id)
    except:
        return
    return await b.adelete()


async def create_order_from_cart(user_id, address) -> Order | None:
    try:
        user = await TGUser.objects.aget(tg_id=user_id)
    except:
        return None
    items = await get_user_cart(user)
    cart = list(map(lambda i: {'pk': i.item.pk,
                               'name': i.item.name,
                               'price': i.item.price,
                               'qty': i.qty},
                    items))
    total_sum = sum(list(map(lambda i: i.get('price', 0)*i.get('qty'), cart)))
    try:
        order = await Order.objects.acreate(user=user, cart=cart, delivery_address=address, summary=total_sum)
    except:
        return None
    # create_xlsx_order(cart, order_no=order.pk, date=order.updated, address=order.delivery_address)
    return order


async def get_order_by_id(order_id) -> Order | None:
    try:
        obj = await Order.objects.aget(pk=order_id)
    except ObjectDoesNotExist:
        obj = None
    return obj


async def clear_user_cart(user):
    try:
        b = CartItem.objects.filter(user=user)
    except:
        return 0
    return await b.adelete()


async def get_faq_questions() -> list[Question]:
    return [item async for item in Question.objects.filter(~Q(answer="") & ~Q(answer__isnull=True))]


async def ask_or_record_question(question) -> Question | None:
    try:
        obj = await Question.objects.aget(name=question)
        await Question.objects.filter(name=question).aupdate(count=obj.count + 1)
    except ObjectDoesNotExist:
        await Question.objects.acreate(name=question)
        return None
    except Exception as e:
        logger.error(e)
        return None
    return obj


async def get_answer_on_question(qst_id) -> Question:
    try:
        obj = await Question.objects.aget(pk=qst_id)
    except ObjectDoesNotExist:
        obj = None
    return obj

