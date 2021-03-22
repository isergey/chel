from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import models


class CategoryAdmin(MPTTModelAdmin):
    pass


admin.site.register(models.Category, CategoryAdmin)


class AgeCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.AgeCategory, AgeCategoryAdmin)


class EventParticipantInline(admin.TabularInline):
    model = models.EventParticipant


class EventAdmin(admin.ModelAdmin):
    inlines = [EventParticipantInline]


admin.site.register(models.Event, EventAdmin)


class EventParticipationReminderAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.EventParticipationReminder, EventParticipationReminderAdmin)
