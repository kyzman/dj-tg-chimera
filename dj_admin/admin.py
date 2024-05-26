import pprint

from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.generic import DetailView

from dj_admin.models import TGUser, ItemGroup, ItemCategory, GoodItem, Question, Order, Mailing


class OrderDetailView(PermissionRequiredMixin, DetailView):
    model = Mailing
    permission_required = "mailing.view_mailing"
    template_name = "admin/dj_admin/mailing/detail.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }


class MailingAdmin(admin.ModelAdmin):
    fields = ('title', 'text', 'media', 'recipients', 'sent')
    list_display = ('title', 'sent', 'apply')
    readonly_fields = ('apply', 'sent')
    filter_horizontal = ('recipients',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.sent:
                return self.readonly_fields + self.fields
        return self.readonly_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ customize edit form """
        if object_id:
            obj = self.model.objects.get(pk=object_id)
            if obj.sent:
                extra_context = extra_context or {}
                extra_context['show_save_and_continue'] = False
                extra_context['show_save'] = False
                extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return self.changeform_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        return [
            path(
                "<pk>/detail",
                self.admin_site.admin_view(OrderDetailView.as_view()),
                name=f"start_mailing",
            ),
            *super().get_urls(),
        ]

    @admin.display(description="Начать рассылку")
    def apply(self, mails: Mailing):
        url = reverse("admin:start_mailing", args=[mails.pk])
        if mails.sent:
            message = format_html("Разослано")
        else:
            message = format_html(f"""<button type="button" onclick="location.href='{url}'">Разослать</button>""")
        return message


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

admin.site.register(Mailing, MailingAdmin)
