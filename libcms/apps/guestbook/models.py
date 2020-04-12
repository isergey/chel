# -*- encoding: utf-8 -*-
from django.conf import settings
from django.db import models

class Feedback(models.Model):
    email = models.EmailField(verbose_name='Email для связи')
    content = models.CharField(max_length=2048, verbose_name='Текст отзыва')
    comment = models.CharField(max_length=10000, verbose_name='Коментарии к отзыву')
    add_date = models.DateTimeField(auto_now=True, verbose_name="Дата написания", db_index=True)
    publicated = models.BooleanField(verbose_name='Опубликовано?', default=False, db_index=True)
    class Meta:
        permissions = (
            ("can_comment", "Can comment feedback"),
            ("can_public", "Can public feedback"),
        )
