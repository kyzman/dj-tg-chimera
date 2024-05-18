from django.contrib import admin

from dj_admin.models import TGUser


class TGUserAdmin(admin.ModelAdmin):
    list_display = ['tg_id', 'created']
    list_filter = ['created', ]
    readonly_fields = ['tg_id']
    search_fields = ['tg_id', ]
    save_on_top = True


admin.site.register(TGUser, TGUserAdmin)