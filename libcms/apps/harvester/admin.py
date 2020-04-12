# -*- coding: utf-8 -*-
from django.contrib import admin
from . import models


# class RecordContentInline(admin.TabularInline):
#     model = models.RecordContent
#
#
# @admin.register(models.Record)
# class RecordAdmin(admin.ModelAdmin):
#     inlines = [RecordContentInline]
#     list_filter = ('create_date', 'update_date')
#     search_fields = ['id', 'original_id']
#     list_display = ('id', 'original_id', 'hash', 'source', 'deleted', 'create_date', 'update_date', 'session_id')
#
#
# class SourceRecordsFileInline(admin.TabularInline):
#     model = models.SourceRecordsFile
#
#
# @admin.register(models.Source)
# class SourceAdmin(admin.ModelAdmin):
#     inlines = [SourceRecordsFileInline]
#     list_display = ('code', 'name', 'reset', 'active', 'create_date')
#
#
# @admin.register(models.HarvestingStatus)
# class HarvestingStatusAdmin(admin.ModelAdmin):
#     list_display = (
#         'source', 'create_date', 'created', 'updated', 'deleted', 'processed', 'total_records', 'error', 'session_id')

@admin.register(models.FullTextCache)
class HarvestingStatusAdmin(admin.ModelAdmin):
    list_display = (
        'uri_hash', 'uri', 'create_date', 'update_date', 'error')