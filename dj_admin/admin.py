from django.contrib import admin

from dj_admin.models import TGUser, ItemGroup, ItemCategory, GoodItem, Question, Order, CartItem


class TGUserAdmin(admin.ModelAdmin):
    list_display = ['tg_id', 'created']
    list_filter = ['created', ]
    readonly_fields = ['tg_id']
    search_fields = ['tg_id', ]
    save_on_top = True


admin.site.register(TGUser, TGUserAdmin)
admin.site.register(ItemGroup)
admin.site.register(ItemCategory)
admin.site.register(GoodItem)
admin.site.register(Question)
admin.site.register(Order)

admin.site.register(CartItem)
# admin.site.register(Cart)
