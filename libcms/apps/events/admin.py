from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from . import models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent', 'order']


admin.site.register(models.Category, CategoryAdmin)


class AgeCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.AgeCategory, AgeCategoryAdmin)


admin.site.register(models.Address, DraggableMPTTAdmin)


class EventParticipantInline(admin.TabularInline):
    model = models.EventParticipant


class EventAdmin(admin.ModelAdmin):
    inlines = [EventParticipantInline]


admin.site.register(models.Event, EventAdmin)


class EventParticipationReminderAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.EventParticipationReminder, EventParticipationReminderAdmin)
