from django.contrib import admin

from .models import Record


class RecordAdmin(admin.ModelAdmin):
    list_display = ('namespace', 'key')


admin.site.register(Record, RecordAdmin)
