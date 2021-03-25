# encoding: utf-8
from django.contrib import admin
from . import models


class ExternalUseAdmin(admin.ModelAdmin):
    list_display = ('user', 'external_username')


admin.site.register(models.ExternalUser, ExternalUseAdmin)
