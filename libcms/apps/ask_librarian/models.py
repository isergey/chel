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
        category_title = CategoryTitle.objects.filter(lang=lang, category=self).first()
        if category_title is None:
            return ''
        return category_title.title

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


class QuestionTarget(models.Model):
    title = models.CharField(verbose_name='Название', max_length=512)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Цели вопросов'
        verbose_name = 'Цель вопроса'


class Education(models.Model):
    title = models.CharField(verbose_name='Название', max_length=512)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Виды образования'
        verbose_name = 'Образование'


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
    STATUS_NEW = 0
    STATUS_DONE = 1
    STATUS_ON_PROCESS = 2

    STATUSES = (
        (STATUS_NEW, 'Новый'),
        (STATUS_DONE, 'Готов'),
        (STATUS_ON_PROCESS, 'В обработке'),
    )

    user = models.ForeignKey(User, null=True, verbose_name='Пользователь', on_delete=models.CASCADE, blank=True)
    fio = models.CharField(verbose_name='ФИО', blank=False, max_length=128, default='')
    email = models.EmailField(verbose_name='email', blank=False, max_length=256)
    city = models.CharField(verbose_name='Город', blank=False, max_length=64)
    country = models.CharField(verbose_name='Страна', blank=True, max_length=64)
    category = models.ForeignKey(Category, null=True, verbose_name='Тематика',
                                 help_text='Укажите тематику, к которой относится вопрос', on_delete=models.PROTECT)
    question_target = models.ForeignKey(
        QuestionTarget,
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name='Цель запроса'
    )

    education = models.ForeignKey(
        Education,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Образование',
    )

    question = models.TextField(max_length=2048, verbose_name='Вопрос')
    answer = models.TextField(max_length=50000, verbose_name='Ответ', blank=True)
    status = models.IntegerField(choices=STATUSES, verbose_name='Статус', db_index=True, default=STATUS_NEW)

    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)
    update_date = models.DateTimeField(auto_now=True, verbose_name='Дата обновления', db_index=True)
    manager = models.ForeignKey(QuestionManager, verbose_name='Менеджер', null=True, blank=True,
                                on_delete=models.CASCADE)
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

    def take_to_process(self, manager, message='', commit=True):
        if self.is_new():
            self.start_process_date = datetime.datetime.now()
            self.manager = manager
            self.status = Question.STATUS_ON_PROCESS
            if commit:
                self.save()
            StatusJournal.objects.bulk_create([
                StatusJournal(question=self, user_id=manager.user_id, status=self.status, message=message)
            ])

    def close_process(self, manager, message='', commit=True):
        if self.is_processing():
            self.end_process_date = datetime.datetime.now()
            self.status = Question.STATUS_DONE
            if commit:
                self.save()
            StatusJournal.objects.bulk_create(
                [StatusJournal(question=self, user_id=manager.user_id, status=self.status, message=message)]
            )

    def edit_process(self, manager, commit=True):
        if commit:
            self.save()
        if self.status != Question.STATUS_ON_PROCESS:
            StatusJournal.objects.bulk_create([
                StatusJournal(question=self, user_id=manager.user_id, status=self.STATUS_ON_PROCESS, message='Редактирование'),
                StatusJournal(question=self, user_id=manager.user_id, status=self.status)
            ])

class StatusJournal(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь сменивший статус', on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=Question.STATUSES, verbose_name='Статус', db_index=True)
    message = models.TextField(
        max_length=10 * 1024,
        blank=True
    )
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)


class Recomendation(models.Model):
    user = models.ForeignKey(User, null=True, verbose_name='Пользователь', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name='Вопрос, к которому относится рекомендация',
                                 on_delete=models.CASCADE)
    text = models.TextField(max_length=2048, verbose_name='Текст рекомендации')
    public = models.BooleanField(default=False, db_index=True, verbose_name='Публиковать Вместе с ответом')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)
