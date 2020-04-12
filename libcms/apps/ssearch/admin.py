from django.contrib import admin

from .models import DetailLog, SearchLog


class SearchLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'params', 'total', 'in_results', 'session_id', 'date_time')


admin.site.register(SearchLog, SearchLogAdmin)


class DetailLogAdmin(admin.ModelAdmin):
    list_display = ('record_id', 'action', 'date_time')


admin.site.register(DetailLog, DetailLogAdmin)
