from django.contrib import admin


from models import DetailLog



class DetailLogAdmin(admin.ModelAdmin):
    list_display = ('record_id', 'action', 'date_time')

admin.site.register(DetailLog, DetailLogAdmin)

