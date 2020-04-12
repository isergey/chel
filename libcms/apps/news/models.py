# -*- encoding: utf-8 -*-
from django.shortcuts import reverse
from django.conf import settings
from django.db import models

NEWS_TYPE_CHOICES = (
    (0, 'Новости ЧОУНБ'),
    (1, 'Новости библиотек области'),
    (2, 'Общие'),
)

class News(models.Model):
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", db_index=True)
    type = models.IntegerField(verbose_name='Вид новостей', default=(0, 'Публичные'), choices=NEWS_TYPE_CHOICES, db_index=True)
    publicated = models.BooleanField(verbose_name='Опубликовано?', default=True, db_index=True)
    avatar_img_name = models.CharField(max_length=100, blank=True, null=True)
    def get_absolute_url(self):
        return reverse('news:frontend:show', args=[self.id])


class NewsContent(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    lang = models.CharField(verbose_name="Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name='Заглавие', max_length=512)
    teaser = models.CharField(verbose_name='Тизер', max_length=512, help_text='Краткое описание новости')
    content = models.TextField(verbose_name='Содержание новости')
    class Meta:
        unique_together = (('news', 'lang'),)

