# -*- encoding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import User
from django.utils.functional import cached_property
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    code = models.SlugField(
        max_length=128,
        primary_key=True,
        verbose_name='Код категории',
        help_text='Разрешены латинские буквы, знаки _ и -'
    )

    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        verbose_name='Родительская категория',
        null=True,
        blank=True
    )

    title = models.CharField(
        verbose_name='Название',
        max_length=1024,
        db_index=True
    )

    order = models.IntegerField(
        verbose_name='Порядок вывода',
        default=0,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-order', 'title']

    def __str__(self):
        return self.title

    def clean(self):
        self.code = self.code.strip().lower()


class AgeCategory(models.Model):
    age = models.IntegerField(
        primary_key=True,
        verbose_name='Возраст (лет)',
        help_text='Укажите возраст, начиная с которого, можно посещать события.'
    )

    def __str__(self):
        return '{age}+'.format(age=str(self.age))

    class Meta:
        verbose_name = 'Возрастная категория'
        verbose_name_plural = 'Возрастные категории'
        ordering = ['age']


class Address(MPTTModel):
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='address_parent'
    )
    title = models.CharField(
        verbose_name='Название места',
        max_length=512,
        db_index=True
    )

    address = models.CharField(
        verbose_name='Адрес',
        max_length=512,
        blank=True
    )

    contacts = models.TextField(
        verbose_name='Контакты',
        max_length=1024,
        blank=True
    )

    geo_latitude = models.FloatField(
        verbose_name='Гео широта',
        default=0
    )

    geo_longitude = models.FloatField(
        verbose_name='Гео долгота',
        default=0
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
        ordering = ['title']


def upload_avatar_handler(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    uid = str(uuid.uuid4())
    uid0 = uid[0]
    uid1 = uid[1]
    uid2 = uid[2]
    uid3 = uid[3]
    return 'events/avatars/{uid0}/{uid1}/{uid2}/{uid3}/{id}{file_extension}'.format(
        uid0=uid0,
        uid1=uid1,
        uid2=uid2,
        uid3=uid3,
        id=uid,
        file_extension=file_extension
    )


class Event(models.Model):
    avatar = models.ImageField(
        verbose_name='Аватарка',
        blank=True,
        upload_to=upload_avatar_handler
    )
    start_date = models.DateTimeField(
        verbose_name='Дата начала',
        null=False,
        blank=False,
        db_index=True
    )

    end_date = models.DateTimeField(
        verbose_name='Дата окончания',
        null=False,
        blank=False,
        db_index=True
    )

    address = models.CharField(
        verbose_name='Подразделение',
        max_length=512,
        blank=True
    )

    address_reference = TreeForeignKey(
        Address,
        on_delete=models.PROTECT,
        verbose_name='Подразделение из справочника',
        blank=True,
        null=True
    )

    active = models.BooleanField(
        verbose_name='Активно',
        default=True,
        db_index=True
    )

    need_registration = models.BooleanField(
        verbose_name='Требуется регистрация',
        default=False,
    )

    category = models.ManyToManyField(
        Category,
        verbose_name='Категории',
        blank=True,
    )

    age_category = models.ForeignKey(
        AgeCategory,
        verbose_name='Возрастная категория',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    keywords = models.CharField(
        verbose_name='Ключевые слова',
        max_length=1024,
        blank=True,
        help_text='Через запятую'
    )

    translation_html = models.TextField(
        verbose_name='HTML код плеера для трансляций или воспроизведения',
        blank=True,
        max_length=10 * 1024
    )

    create_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата создания',
        db_index=True
    )

    class Meta:
        verbose_name = 'мероприятие'
        verbose_name_plural = 'мероприятия'

    def splited_keywords(self):
        keywords = []

        for keyword in self.keywords.split(','):
            keywords.append(keyword.strip())
        return keywords

    @cached_property
    def content(self):
        return EventContent.objects.filter(event=self).first()


class EventContent(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    lang = models.CharField(
        verbose_name='Язык',
        db_index=True,
        max_length=2,
        choices=settings.LANGUAGES
    )

    title = models.CharField(
        verbose_name='Заглавие',
        max_length=512
    )

    teaser = models.CharField(
        verbose_name='Тизер',
        max_length=512
    )

    content = models.TextField(
        verbose_name='Описание события'
    )

    class Meta:
        unique_together = (('event', 'lang'),)


class EventParticipant(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=256
    )

    first_name = models.CharField(
        verbose_name='Имя Отчество',
        max_length=256
    )

    reader_id = models.CharField(
        verbose_name='№ читательского билета',
        max_length=256
    )

    email = models.EmailField(
        verbose_name='Email',
        max_length=256
    )

    create_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата создания',
        db_index=True
    )

    class Meta:
        verbose_name = 'Участник мероприятия'
        verbose_name_plural = 'Участники мероприятий'
        unique_together = [['user', 'event']]


class EventParticipationReminder(models.Model):
    TYPE_EMAIL = 'email'
    TYPE_SMS = 'sms'

    TYPES = (
        (TYPE_EMAIL, 'по электронной почте'),
        (TYPE_SMS, 'sms')
    )

    event_participant = models.ForeignKey(
        EventParticipant,
        on_delete=models.CASCADE,
        verbose_name='Участник'
    )

    remind_date = models.DateTimeField(
        verbose_name='Время напоминания',
        db_index=True
    )

    type = models.CharField(
        verbose_name='Тип напоминияния',
        choices=TYPES,
        default=TYPE_EMAIL,
        max_length=64
    )

    is_sent = models.BooleanField(
        verbose_name='Отправлено',
        default=False,
        db_index=True
    )

    created = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата создания',
        db_index=True
    )

    class Meta:
        verbose_name = 'Напоминания об участии'
        verbose_name_plural = 'Напоминания об участии'

    def clean(self):
        # if EventParticipationReminder.objects.filter(event_participant=self.event_participant).count() > 3:
        #     raise ValidationError('Превышен лимит допустимых напоминаний на одно событие')

        if self.remind_date > self.event_participant.event.start_date:
            raise ValidationError('Время напоминания не может быть позде времени начала события')


class FavoriteEvent(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'отмеченное мероприятие'
        verbose_name_plural = 'отмеченные мероприятия'
        unique_together = [['user', 'event']]


class EventRemember(models.Model):
    favorite_event = models.ForeignKey(
        FavoriteEvent,
        verbose_name='Избранное событие',
        on_delete=models.CASCADE
    )

    remember_date = models.DateField(
        verbose_name='Дата напоминания',
        blank=True,
        null=True
    )

    remember_system = models.IntegerField(
        verbose_name='Система напоминания (0-email, 1-sms)',
        default=0
    )


class EventComment(models.Model):
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    text = models.CharField(
        verbose_name='Текст комментария (макс. 1024 символа)',
        max_length=1024,
        null=False,
        blank=False
    )

    post_date = models.DateTimeField(
        verbose_name='Дата отправления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
