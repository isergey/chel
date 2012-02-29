# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Forum(models.Model):
    title = models.CharField(max_length=255, verbose_name=_(u'Title'), help_text=_(u'Maximum 255 simbols'))
    slug = models.SlugField(unique=True, verbose_name=_(u'Slug'), help_text=_(u'Small latin letter, "-" and "_"'))
    description = models.CharField(max_length=1024, verbose_name=_(u'Description'), help_text=_(u'Maximum 1024 simbols'))
    ordering = models.IntegerField(default=0, verbose_name=_(u'Ordering'), db_index=True, help_text=_(u'Order in forums list'))
    closed = models.BooleanField(verbose_name=_(u'Closed'), db_index=True, default=False, help_text=_(u'If forum is closed, users can not create topics'))

    class Meta:
        ordering = ['ordering',]
        permissions = (("view_forum", "Can view forum"),)

    def __unicode__(self):
        return self.title



class Topic(models.Model):
    forum = models.ForeignKey(Forum)
    subject = models.CharField(verbose_name=_(u'Subject'), max_length=255, help_text=_(u'Maximum 255 simbols'))
    created = models.DateTimeField(default=datetime.now, db_index=True, verbose_name=_(u'Created'))
    public = models.BooleanField(verbose_name=_(u'Publicated'), db_index=True, default=True)
    closed = models.BooleanField(verbose_name=_(u'Closed'), db_index=True, default=False, help_text=_(u'If topic is closed, users can not create messages'))

    class Meta:
        ordering = ['-id']
        permissions = (("view_topic", "Can view forum topic"),)


class Article(models.Model):
    topic = models.ForeignKey(Topic)
    author = models.ForeignKey(User, blank=True, null=True, verbose_name=_(u'Author'))
    text = models.TextField(verbose_name=_(u'Text of message'), max_length=10000, help_text=_(u'Maximum 10000 simbols'))
    created = models.DateTimeField(default=datetime.now, db_index=True, verbose_name=_(u'Created'))
    updated = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_(u'Created'))
    public = models.BooleanField(verbose_name=u'Publicated', db_index=True, default=True)

    class Meta:
        ordering = ['created']
        permissions = (("view_article", "Can view forum message"),)

    def __unicode__(self):
        return u'(%s, %s)' % (self.topic, self.author)

