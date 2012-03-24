# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Permissions(User):
    """
    Класс для создания прав достпа
    """
    class Meta:
        proxy = True
        permissions = (
            ("view_page", "Can view page"),
            ("public_page", "Can public page"),
        )




class Page(MPTTModel):
    parent = TreeForeignKey('self',null=True, blank=True, related_name='children', verbose_name=u'Родительская страница')
    slug = models.SlugField(verbose_name=u'Slug', max_length=255, db_index=True, unique=True)
    public = models.BooleanField(verbose_name=u'Опубликована?', default=False, db_index=True, help_text=u'Публиковать страницу могут только пользователи с правами публикации страниц')
    create_date = models.DateTimeField(verbose_name=u"Дата создания", auto_now_add=True, db_index=True)
    class Meta:
        ordering = ['-create_date']

    def __unicode__(self):
        return  self.slug


class Content(models.Model):
    page = models.ForeignKey(Page, verbose_name=u'Родительская страница')
    lang = models.CharField(verbose_name=u"Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name=u'Заглавие', max_length=512)
    meta = models.CharField(verbose_name=u"SEO meta", max_length=512, blank=True, help_text=u'Укажите ключевые слова для страницы, желательно на языке контента')
    content = models.TextField(verbose_name=u'Контент')

    class Meta:
        unique_together = (('page', 'lang'),)

    def __unicode__(self):
        return self.title


    def return_in_lang(self):
        pass