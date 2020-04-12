# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.utils.translation import get_language

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User


class AskLibraryError(Exception):
    pass


class Category(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children',
                            verbose_name='Родительский элемент', on_delete=models.CASCADE)

    def get_t_ancestors(self):
        """
        return translated ancestors
        """
        ancestors = list(self.get_ancestors())
        lang = get_language()[:2]
        items = CategoryTitle.objects.filter(category__in=ancestors, lang=lang)
        return items

    def get_t_descendants(self):
        descendants = list(self.descendants())
        lang = get_language()[:2]
        items = CategoryTitle.objects.filter(category__in=descendants, lang=lang)
        return items

    def title(self):
        lang = get_language()[:2]
        return CategoryTitle.objects.get(lang=lang, category=self).title

    def __str__(self):
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    lang = models.CharField(verbose_name="Язык", db_index=True, max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(verbose_name='Название', max_length=512)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (('category', 'lang'),)


QUESTION_STATUSES = (
    (0, 'Новый'),
    (1, 'Готов'),
    (2, 'В обработке'),
)


class QuestionManager(models.Model):
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    available = models.BooleanField(verbose_name='Доступен?', default=False, db_index=True)

    class Meta:
        verbose_name = "Менеджер вопросов"
        verbose_name_plural = "Менеджеры вопросов"

    @staticmethod
    def get_manager(user):
        try:
            manager = QuestionManager.objects.get(user=user)
        except QuestionManager.DoesNotExist:
            return None
        return manager


class Question(models.Model):
    user = models.ForeignKey(User, null=True, verbose_name='Пользователь', on_delete=models.CASCADE)
    fio = models.CharField(verbose_name='ФИО', blank=True, max_length=128, default='')
    email = models.EmailField(verbose_name='email', blank=True, max_length=256,
                              help_text='На этот адрес будет выслан ответ на вопрос')
    city = models.CharField(verbose_name='Город', blank=True, max_length=64)
    country = models.CharField(verbose_name='Страна', blank=True, max_length=64)
    category = models.ForeignKey(Category, null=True, verbose_name='Тематика',
                                 help_text='Укажите тематику, к которой относиться вопрос', on_delete=models.CASCADE)
    question = models.TextField(max_length=2048, verbose_name='Вопрос')
    answer = models.TextField(max_length=50000, verbose_name='Ответ')
    status = models.IntegerField(choices=QUESTION_STATUSES, verbose_name='Статус', db_index=True, default=0)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)

    manager = models.ForeignKey(QuestionManager, verbose_name='Менеджер', null=True, blank=True, on_delete=models.CASCADE)
    start_process_date = models.DateTimeField(blank=True, null=True, db_index=True,
                                              verbose_name='Дата взятия вопроса на обработку')
    end_process_date = models.DateTimeField(blank=True, null=True, db_index=True,
                                            verbose_name='Дата окончания обработки вопроса')

    def __str__(self):
        return self.question

    def is_ready(self):
        if self.status == 1:
            return True
        else:
            return False

    def is_processing(self):
        if self.status == 2:
            return True
        else:
            return False

    def is_new(self):
        if self.status == 0:
            return True
        else:
            return False

    def take_to_process(self, manager, commit=True):
        if self.is_new():
            self.start_process_date = datetime.datetime.now()
            self.manager = manager
            self.status = 2
            if commit:
                self.save()

    def close_process(self, commit=True):
        if self.is_processing():
            self.end_process_date = datetime.datetime.now()
            self.status = 1
            if commit:
                self.save()


class Recomendation(models.Model):
    user = models.ForeignKey(User, null=True, verbose_name='Пользователь', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='Вопрос, к которому относиться рекомендация', on_delete=models.CASCADE)
    text = models.TextField(max_length=2048, verbose_name='Текст рекомендации')
    public = models.BooleanField(default=False, db_index=True, verbose_name='Публиковать Вместе с ответом')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)
