# encoding: utf-8

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Group(models.Model):
    name = models.CharField(verbose_name='Группа рассылок', max_length=255, unique=True)
    order = models.IntegerField(verbose_name='Порядок вывода группы', default=0)
    hidden = models.BooleanField(verbose_name='Скрыть', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа расылок'
        verbose_name_plural = 'Группы рассылок'
        ordering = ['-order', 'name']


class Subscribe(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, verbose_name='Группа рассылок', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name='Название рассылки', max_length=255)
    code = models.SlugField(verbose_name='Код рассылки', unique=True, max_length=32, db_index=True)
    description = models.TextField(verbose_name='Описание', max_length=20000, blank=True)
    lucene_query = models.TextField(
        verbose_name='Поисковый запрос',
        max_length=10 * 1024,
        blank=True,
        help_text='Поисковый запрос в формате Lucene',
    )
    send_only_by_code = models.BooleanField(
        verbose_name='Отпралять только по коду',
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(verbose_name='Активна', default=True, db_index=True)
    hidden = models.BooleanField(verbose_name='Скрыть', default=False)

    def __str__(self):
        return self.name

    class Meta:
        # ordering = ['order', 'name']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


CONTENT_FORMAT_CHOICES = (
    ('text', "Текст"),
    ('html', "HTML"),
)

BROADCAST_STATUS = (
    (False, 'только подписчикам рассылки'),
    (True, 'всем пользователям с email'),
)

class Subscriber(models.Model):
    subscribe = models.ManyToManyField(Subscribe, verbose_name='Подписки')
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text='Будет использоваться email пользователя'
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        db_index=True,
        unique=True,
        help_text='На этот адрес будут приходить письма рассылки', blank=True
    )
    is_active = models.BooleanField(verbose_name='Активный', default=True, db_index=True)
    create_date = models.DateTimeField(verbose_name='Дата создания', db_index=True, auto_now_add=True)

    def clean(self):
        if not self.email and self.user:
            self.email = self.user.email

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class Letter(models.Model):
    subscribe = models.ForeignKey(Subscribe, verbose_name='Рассылка', on_delete=models.CASCADE)
    to_subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        verbose_name='Подписчику',
        null=True,
        blank=True,
        help_text='Если указан, письмо будет направлено персонально подписчику'
    )
    broadcast = models.BooleanField(
        verbose_name='Отправить',
        default=False,
        choices=BROADCAST_STATUS,
        help_text=''
    )
    subject = models.CharField(verbose_name='Тема', max_length=255)
    content_format = models.CharField(verbose_name='Формат письма', max_length=16, choices=CONTENT_FORMAT_CHOICES)
    content = models.TextField(verbose_name='Содержимое')
    send_completed = models.BooleanField(verbose_name='Доставлено всем получателям', db_index=True, default=False)
    must_send_at = models.DateTimeField(verbose_name='Время отправки', db_index=True, default=timezone.now)
    create_date = models.DateTimeField(verbose_name='Дата создания', db_index=True, auto_now_add=True)

    def __str__(self):
        return '%s: %s' % (str(self.subscribe), self.subject)

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'
        ordering = ['-create_date']


class SendStatus(models.Model):
    subscriber = models.ForeignKey(
        Subscriber,
        verbose_name='Подписчик',
        null=True, blank=True,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    letter = models.ForeignKey(Letter, verbose_name='Письмо', on_delete=models.CASCADE)
    is_sent = models.BooleanField(verbose_name='Отпарвлено', default=False, db_index=True)
    has_error = models.BooleanField(verbose_name='Ошибка при отправлении', default=False, db_index=True)
    error_message = models.CharField(verbose_name='Диагностика', max_length=255, blank=True)
    create_date = models.DateTimeField(verbose_name='Дата создания', db_index=True, auto_now_add=True)

    class Meta:
        verbose_name = 'Статус отправки письма'
        verbose_name_plural = 'Статусы отправки писем'
        # unique_together = (('subscriber', 'letter'), ('user', 'letter'))
        ordering = ['-create_date']

    def clean(self):
        if not self.subscriber_id and not self.user_id:
            raise ValidationError('Необходимо указать либо подписчика либо пользователя')


SUBSCRIBING_LOG_ACTIONS = {
    'subscribe': 1,
    'unsubscribe': 2
}

SUBSCRIBING_LOG_ACTIONS_CHOICES = (
    (SUBSCRIBING_LOG_ACTIONS['subscribe'], 'Подписка'),
    (SUBSCRIBING_LOG_ACTIONS['unsubscribe'], 'Отписка'),
)


class SubscribingLog(models.Model):
    subscribe = models.ForeignKey(
        Subscribe,
        verbose_name='Подписка',
        null=True,
        on_delete=models.SET_NULL
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        null=True,
        on_delete=models.SET_NULL
    )
    action = models.IntegerField(
        verbose_name='Действие',
        choices=SUBSCRIBING_LOG_ACTIONS_CHOICES
    )
    create_date = models.DateTimeField(
        verbose_name='Дата записи',
        db_index=True,
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Журнал подписок'
        verbose_name_plural = 'Журнал подписок'


def get_subscribe_titles(ids):
    reference = {}
    for subscribe in Subscribe.objects.filter().values('id', 'name'):
        reference[subscribe.get('id')] = subscribe.get('name')
    return reference


def get_actions_title():
    reference = {}
    for action_choice in SUBSCRIBING_LOG_ACTIONS_CHOICES:
        reference[action_choice[0]] = action_choice[1]
    return reference


