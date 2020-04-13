from django.contrib import admin
from . import models
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(models.ContentType, ContentTypeAdmin)