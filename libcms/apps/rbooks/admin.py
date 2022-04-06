from django.contrib import admin
from . import models


class ViewLogAdmin(admin.ModelAdmin):
    list_display = ('doc_id', 'collection', 'view_dt', 'user_id')


admin.site.register(models.ViewLog, ViewLogAdmin)
