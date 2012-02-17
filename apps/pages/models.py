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
    parent = TreeForeignKey('self',null=True, blank=True, related_name='children', verbose_name=_(u'Parent page'))
    slug = models.SlugField(verbose_name=_(u'Latin title'), max_length=255, db_index=True, unique=True)
    public = models.BooleanField(verbose_name=_(u'Public'), default=False, db_index=True)
    create_date = models.DateTimeField(verbose_name=_(u"Create date"), auto_now_add=True, db_index=True)
    class Meta:
        ordering = ['-create_date']

    def __unicode__(self):
        return  self.slug

class Translate(models.Model):
    page = models.ForeignKey(Page, verbose_name=_(u'Page owner'))
    lang = models.CharField(verbose_name=u"Language", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name=_(u'Title'), max_length=512)
    meta = models.CharField(verbose_name=_(u"SEO meta"), max_length=512)
    content = models.TextField(verbose_name=_(u'Content'))

    class Meta:
        unique_together = (('page', 'lang'),)

    def __unicode__(self):
        return self.title