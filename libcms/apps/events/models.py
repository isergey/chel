# -*- encoding: utf-8 -*-
from django.conf import settings
from django.db import models

from django.contrib.auth.models import User


class Event(models.Model):
    start_date = models.DateTimeField(verbose_name="Дата начала",
                                      null=False, blank=False, db_index=True)
    end_date = models.DateTimeField(verbose_name="Дата окончания",
                                    null=False, blank=False, db_index=True)
    address = models.CharField(verbose_name="Место проведения",
                               max_length=512, blank=True)
    active = models.BooleanField(verbose_name="Активно",
                                 default=True, db_index=True)
    create_date = models.DateTimeField(auto_now=True, verbose_name="Дата создания", db_index=True)

    class Meta:
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"


class EventContent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    lang = models.CharField(verbose_name="Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name='Заглавие', max_length=512)
    teaser = models.CharField(verbose_name='Тизер', max_length=512)
    content = models.TextField(verbose_name='Описание события')

    class Meta:
        unique_together = (('event', 'lang'),)


class FavoriteEvent(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, verbose_name="Мероприятие", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "отмеченное мероприятие"
        verbose_name_plural = "отмеченные мероприятия"


class EventRemember(models.Model):
    favorite_event = models.ForeignKey(FavoriteEvent, verbose_name="Избранное событие", on_delete=models.CASCADE)
    remember_date = models.DateField(verbose_name="Дата напоминания", blank=True, null=True)
    remember_system = models.IntegerField(verbose_name="Система напоминания (0-email, 1-sms)", default=0)


class EventComment(models.Model):
    event = models.ForeignKey(Event, verbose_name="Мероприятие", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    text = models.CharField(verbose_name="Текст комментария (макс. 1024 символа)",
                            max_length=1024, null=False, blank=False)
    post_date = models.DateTimeField(verbose_name="Дата отправления",
                                     auto_now_add=True)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"
