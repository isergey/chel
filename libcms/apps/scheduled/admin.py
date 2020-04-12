from django.contrib import admin
from .models import Scheduler


@admin.register(Scheduler)
class SchedulerAdmin(admin.ModelAdmin):
    pass
