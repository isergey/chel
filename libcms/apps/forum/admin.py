from django.contrib import admin


from models import Forum, Topic, Article



class ForumAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Forum, ForumAdmin)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('subject',)

admin.site.register(Topic, TopicAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('text',)

admin.site.register(Article, ArticleAdmin)