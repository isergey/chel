from django.contrib import admin

from . import models


class SubscribeGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(models.Group, SubscribeGroupAdmin)


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'order')


admin.site.register(models.Subscribe, SubscribeAdmin)


class LetterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'subscribe', 'send_completed', 'must_send_at', 'create_date')


admin.site.register(models.Letter, LetterAdmin)


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'is_active', 'create_date')


admin.site.register(models.Subscriber, SubscriberAdmin)


class SendStatusAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'letter', 'is_sent', 'create_date')


admin.site.register(models.SendStatus, SendStatusAdmin)


class SubscribingLogAdmin(admin.ModelAdmin):
    list_display = ('subscribe', 'user', 'action', 'create_date')


admin.site.register(models.SubscribingLog, SubscribingLogAdmin)

#
# class JournalAdmin(admin.ModelAdmin):
#     list_display = ('name', 'ordering', 'action', 'create_date')
#
# admin.site.register(models.Journal, SubscribingLogAdmin)
