from django.contrib import admin
from .models import News, NewsContent


class NewsContentInline(admin.StackedInline):
    model = NewsContent
    extra = 1


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    inlines = [NewsContentInline]
