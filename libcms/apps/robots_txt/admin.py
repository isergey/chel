# encoding: utf-8
from django.contrib import admin
import models


class RobotsTxtAdmin(admin.ModelAdmin):
    list_display = ('id',)


admin.site.register(models.RobotsTxt, RobotsTxtAdmin)
