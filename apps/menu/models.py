# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

#class Permissions(User):
#    """
#    Класс для создания прав достпа
#    """
#    class Meta:
#        proxy = True
#        permissions = (
#            ("view_page", "Can view page"),
#            ("public_page", "Can public page"),
#        )


class MenuItem(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_(u'Parent item'))
    url = models.CharField(verbose_name=u'URL', max_length=1024, default='#')
    show = models.BooleanField(verbose_name=u"Show item", default=True, db_index=True)



class MenuItemTitle(models.Model):
    item = models.ForeignKey(MenuItem)
    lang = models.CharField(verbose_name=u"Language", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name=_(u'Title'), max_length=512)

    def __unicode__(self):
        return self.title

class Menu(models.Model):
    slug = models.SlugField(verbose_name=_(u'Slug'), max_length=64, unique=True)
    root_item = models.ForeignKey(MenuItem)



class MenuTitle(models.Model):
    menu = models.ForeignKey(Menu)
    lang = models.CharField(verbose_name=u"Language", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name=_(u'Title'), max_length=512)


