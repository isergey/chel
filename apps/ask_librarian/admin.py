from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from models import Category, Question, Answer, AnswerLanguage, AnswerManager, ManagerNonActivePeriod

admin.site.register(Category, MPTTModelAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)

admin.site.register(Question,QuestionAdmin)




class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'manager', 'create_date', 'text')

admin.site.register(Answer,AnswerAdmin)



class AnswerLanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(AnswerLanguage,AnswerLanguageAdmin)



class AnswerManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'surname', 'phone')

admin.site.register(AnswerManager,AnswerManagerAdmin)




class ManagerNonActivePeriodAdmin(admin.ModelAdmin):
    list_display = ('manager', 'start', 'end', 'reason')

admin.site.register(ManagerNonActivePeriod,ManagerNonActivePeriodAdmin)


