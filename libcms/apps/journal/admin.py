from django.contrib import admin
from .models import Record


class RecordAdmin(admin.ModelAdmin):
    list_display = ['action', 'ip', 'sc', 'user_id', 'created']


admin.site.register(Record, RecordAdmin)
