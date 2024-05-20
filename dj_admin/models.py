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


# class PersonManager(models.Manager):
#     async def get_by_natural_key(self, first_name, last_name):
#         return await self.aget(first_name=first_name, last_name=last_name)


class CartItem(TimeBasedModel):
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE, to_field='tg_id')
    item = models.ForeignKey(GoodItem, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1, blank=True)

    # objects = PersonManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'item'], name='ck_user_item')
        ]



# class Cart(models.Model):
#     user = models.ForeignKey(TGUser, unique=True, on_delete=models.CASCADE)
#     basket = models.ManyToManyField(CartItem, blank=True)
#     delivery_address = models.CharField(max_length=255, blank=True, null=True)


class Question(TimeBasedModel):
    title = models.CharField(max_length=512)
    answer = models.TextField()
    count = models.PositiveIntegerField(default=1, blank=True)


class Order(TimeBasedModel):
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE)
    cart = models.ManyToManyField(CartItem, blank=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    summary = models.PositiveIntegerField(default=0)
