from django.contrib import admin

from . import models


class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'new', 'creation_date', 'changed_date', 'ip_address')


admin.site.register(models.ContactRequest, ContactRequestAdmin)


class NotificationEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'comments')


admin.site.register(models.NotificationEmail, NotificationEmailAdmin)
