from django.contrib import admin

from .models import Version


class VersionAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('content_type', 'content_id', 'user', 'created')


admin.site.register(Version, VersionAdmin)