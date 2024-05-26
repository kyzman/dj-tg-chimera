import pprint

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models


class TimeBasedModel(models.Model):
    class Meta:
        abstract = True
        ordering = ('-created',)

    created = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='дата обновления')


class TGUser(TimeBasedModel):
    tg_id = models.BigIntegerField(unique=True, primary_key=True, db_index=True, verbose_name='id Telegram')
    username = models.CharField(max_length=32, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.tg_id} ({self.username})'


class ItemGroup(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class ItemCategory(models.Model):
    name = models.CharField(max_length=32)
    group = models.ForeignKey(ItemGroup, on_delete=models.PROTECT, verbose_name='Группа товаров')

    def __str__(self):
        return f"{self.name} ({self.group})"


class GoodItem(models.Model):
    name = models.CharField(max_length=32)
    desc = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')
    price = models.IntegerField()
    cat = models.ForeignKey(ItemCategory, on_delete=models.PROTECT, verbose_name='Категория товаров')

    def __str__(self):
        return self.name


class CartItem(TimeBasedModel):
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE, to_field='tg_id')
    item = models.ForeignKey(GoodItem, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'item'], name='ck_user_item')
        ]

    def __str__(self):
        return f"[{self.user}] {self.item}"


class Question(TimeBasedModel):
    name = models.CharField(max_length=512)
    answer = models.TextField(null=True, blank=True)
    count = models.PositiveIntegerField(default=1, blank=True)

    def __str__(self):
        return f"{self.name} [{self.count}]"


class Order(TimeBasedModel):
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE)
    cart = models.JSONField(blank=True, null=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    summary = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"[{self.pk}] {self.delivery_address} от {self.updated.strftime('%d-%m-%Y %H:%M:%S')}"


class Mailing(TimeBasedModel):
    recipients = models.ManyToManyField(User, blank=True, verbose_name="Получатели")
    title = models.CharField(max_length=255, verbose_name="Тема сообщения")
    text = models.TextField(verbose_name="Содержание(текст) рассылки")
    media = models.ImageField(upload_to="mailing/", blank=True, null=True, verbose_name="Вложенное изображение")
    sent = models.BooleanField(default=False, verbose_name="Разослана")

    def __str__(self):
        return f"{self.title} [{self.created.strftime('%d-%m-%Y %H:%M:%S')}]"

    class Meta:
        verbose_name = 'Рассылку'
        verbose_name_plural = 'Рассылки'

    @property
    def start_mailing(self):
        recipients = [i.email for i in self.recipients.all()]
        if self.sent:
            return f"Рассылка была осуществлена {self.updated.strftime('%d-%m-%Y %H:%M:%S')}"
        else:
            self.sent = True
            mail = EmailMessage(subject=self.title, body=self.text, to=recipients)
            if self.media:
                attach = self.media.path
                mail.attach_file(attach)
            self.save()
            return f"Отправлено писем {mail.send()}"
