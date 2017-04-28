# -*- encoding: utf-8 -*-
from django.conf import settings
from django.db import models

from django.contrib.auth.models import User

class Event(models.Model):

    start_date = models.DateTimeField(verbose_name=u"Дата начала",
        null=False, blank=False, db_index=True)
    end_date = models.DateTimeField(verbose_name=u"Дата окончания",
        null=False, blank=False, db_index=True)
    address = models.CharField(verbose_name=u"Место проведения",
        max_length=512, blank=True)
    active = models.BooleanField(verbose_name=u"Активно",
        default=True, db_index=True)
    create_date = models.DateTimeField(auto_now=True, verbose_name=u"Дата создания", db_index=True)

    class Meta:
        verbose_name = u"мероприятие"
        verbose_name_plural = u"мероприятия"


class EventContent(models.Model):
    event = models.ForeignKey(Event)
    lang = models.CharField(verbose_name=u"Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name=u'Заглавие', max_length=512)
    teaser = models.CharField(verbose_name=u'Тизер', max_length=512)
    content = models.TextField(verbose_name=u'Описание события')
    class Meta:
        unique_together = (('event', 'lang'),)



class FavoriteEvent(models.Model):
    user = models.ForeignKey(User, verbose_name=u"Пользователь")
    event = models.ForeignKey(Event, verbose_name=u"Мероприятие")


    class Meta:
        verbose_name = u"отмеченное мероприятие"
        verbose_name_plural = u"отмеченные мероприятия"


class EventRemember(models.Model):
    favorite_event = models.ForeignKey(FavoriteEvent, verbose_name=u"Избранное событие")
    remember_date = models.DateField(verbose_name=u"Дата напоминания", blank=True, null=True)
    remember_system = models.IntegerField(verbose_name=u"Система напоминания (0-email, 1-sms)",default=0)

class EventComment(models.Model):
    event = models.ForeignKey(Event, verbose_name=u"Мероприятие")
    user = models.ForeignKey(User, verbose_name=u"Пользователь")
    text = models.CharField(verbose_name=u"Текст комментария (макс. 1024 символа)",
        max_length=1024, null=False, blank=False)
    post_date = models.DateTimeField(verbose_name=u"Дата отправления",
        auto_now_add=True)
    class Meta:
        verbose_name = u"комментарий"
        verbose_name_plural = u"комментарии"