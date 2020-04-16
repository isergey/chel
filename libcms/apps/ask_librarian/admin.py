from django.contrib import admin

from .models import QuestionManager, QuestionTarget, Question, Education


@admin.register(QuestionManager)
class QuestionManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'available')


@admin.register(QuestionTarget)
class QuestionTargetAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category')
    list_filter = ['category']
    raw_id_fields = ['user']
