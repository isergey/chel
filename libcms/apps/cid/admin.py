# encoding: utf-8

from django.contrib import admin

from django.contrib.admin import DateFieldListFilter
from .models import ImportantDate, Type


class ImportantDateAdmin(admin.ModelAdmin):
    list_display = ["date", 'description']
    list_filter = (
        ('date', DateFieldListFilter),
)
admin.site.register(ImportantDate, ImportantDateAdmin)

class TypeAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

admin.site.register(Type, TypeAdmin)


