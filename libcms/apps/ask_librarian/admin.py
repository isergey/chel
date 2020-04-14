from django.contrib import admin

from .models import QuestionManager, QuestionTarget, Question


class QuestionManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'available')


admin.site.register(QuestionManager, QuestionManagerAdmin)


class QuestionTargetAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(QuestionTarget, QuestionTargetAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category')
    list_filter = ['category']
    raw_id_fields = ['user']


admin.site.register(Question, QuestionAdmin)
