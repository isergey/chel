# -*- coding: utf-8 -*-
from django.utils import timezone
from django.db import models
import datetime
POLL_TYPE_CHOICES = (
    ('radio', "Радио"),
    ('checkboxes', "Галочки"),
)
class Poll(models.Model):
    question = models.CharField(verbose_name="Вопрос",
        max_length=255, null=False, blank=False)

    multi_vote = models.BooleanField(verbose_name="Возможность голосовать несколько раз",
        null=False, blank=False, default=False, choices=((False, "Нет"),(True, "Да")))

    poll_type = models.CharField(verbose_name="Тип голосования",
        help_text='Радио - можно голосовать за один вариант. Галочки - за несколько.',
        max_length=16, choices=POLL_TYPE_CHOICES, default='radio')

    show_results_on_vote = models.BooleanField(verbose_name="Показывать результаты после ответа",
        null=False, blank=False, default=False)

    published = models.BooleanField(verbose_name="Опубликовано",
        null=False, blank=False, db_index=True)

    start_poll_date = models.DateTimeField(verbose_name="Дата начала голосования",
        null=False, blank=False, db_index=True)

    end_poll_date = models.DateTimeField(verbose_name="Дата окончания голосования",
        null=False, blank=False, db_index=True)

    show_results_after_end_poll = models.BooleanField(verbose_name="Показывать результаты после даты окончания голосования",
        null=False, blank=False, default=False)

    def is_active(self):
        now = timezone.now()
        return now >= self.start_poll_date and now < self.end_poll_date


    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "голосование"
        verbose_name_plural = "голосования"
        permissions = (
            ('can_vote', 'Может голосовать'),
            ('can_view_results', 'Может просматривать результаты'),
            )

class Choice(models.Model):
    poll = models.ForeignKey(Poll, verbose_name="Голосование", on_delete=models.CASCADE)
    choice = models.CharField(verbose_name="Вариант ответа",
        max_length=255, null=False, blank=False)
    votes = models.IntegerField(verbose_name="Количество голосов", default=0)
    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = "вариант ответа"
        verbose_name_plural = "варианты ответов"


class PolledUser(models.Model):
    poller_id = models.CharField(max_length=32,
        verbose_name="Идентификатор сессии (md5) или имя пользователя",
        db_index=True)

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)