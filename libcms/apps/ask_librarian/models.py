# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import get_language

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User


class Category(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'Родительский элемент')


    def get_t_ancestors(self):
        """
        return translated ancestors
        """
        ancestors = list(self.get_ancestors())
        lang=get_language()[:2]
        items = CategoryTitle.objects.filter(category__in=ancestors, lang=lang)
        return items

    def title(self):
        lang=get_language()[:2]
        return CategoryTitle.objects.get(lang=lang, category=self).title

    def __unicode__(self):
        return self.title()

    def up(self):
        previous = self.get_previous_sibling()
        if previous:
            self.move_to(previous, position='left')

    def down(self):
        next = self.get_next_sibling()
        if next:
            self.move_to(next, position='right')

class CategoryTitle(models.Model):
    category = models.ForeignKey(Category)
    lang = models.CharField(verbose_name=u"Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name=u'Название', max_length=512)


    def __unicode__(self):
        return self.title
    class Meta:
        unique_together = (('category', 'lang'),)



QUESTION_STATUSES = (
    (0, u'Новый'),
    (1, u'Обрабатывается'),
    (2, u'Обработан'),
)

class Question(models.Model):
    user = models.ForeignKey(User, null=True, verbose_name=u'Пользователь')
    category = models.ForeignKey(Category, null=True, verbose_name=u'Тематика')
    question = models.TextField(max_length=2048, verbose_name=u'Вопрос')
    answer = models.TextField(max_length=10000, verbose_name=u'Ответ')
    status = models.IntegerField(choices=QUESTION_STATUSES, verbose_name=u'Статус', db_index=True, default=0)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания', db_index=True)

