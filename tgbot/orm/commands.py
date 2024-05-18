# Не оптимизировать импорты и не менять их порядок

import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_config.settings")
os.environ.update({'DJANGO_ALLOW_ASYNC_UNSAFE': "true"})
django.setup()

import logging

from asgiref.sync import sync_to_async

from dj_admin.models import TGUser

logger = logging.getLogger(__name__)


# @sync_to_async
async def add_or_update_user(data: dict) -> TGUser:
    user, created = await TGUser.objects.aupdate_or_create(**data)
    if created:
        logger.info(f"user {user.tg_id} ({user.username}) was added to DB")
    else:
        logger.info(f"User {user.tg_id} ({user.username}) was updated")
    return user
