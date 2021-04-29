# encoding: utf-8
import hashlib
from typing import List
from urllib.parse import quote

import bs4
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import models
from django.db import transaction
from django.shortcuts import resolve_url
from django.template import Context, Template
from django.template.loader import get_template
from django.utils import timezone
from mptt.models import MPTTModel

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SUBSCRIBE_FROM_EMAIL = getattr(settings, 'SUBSCRIBE_FROM_EMAIL', 'subscribe@localhost')
SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost')
SECRET_KEY = getattr(settings, 'SECRET_KEY', '')

letter_template = get_template('subscribe/letter/base.html')


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
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
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


class Letter(models.Model):
    subscribe = models.ForeignKey(Subscribe, verbose_name='Рассылка', on_delete=models.CASCADE)
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


#
# class SearchQuerySubscribe(models.Model):
#     name = models.CharField(
#         verbose_name='Название',
#         max_length=512,
#         db_index=True
#     )
#
#     description = models.TextField(
#         verbose_name='Описание',
#         max_length=4 * 1024,
#         blank=True,
#     )
#
#     search_query = models.TextField(
#         verbose_name='Поисковый запрос',
#         max_length=4 * 1024,
#         blank=True
#     )
#     published = models.BooleanField(
#         verbose_name='Опубликовано',
#         db_index=True,
#         default=True,
#     )
#     ordering = models.PositiveIntegerField(
#         verbose_name='Сортировка',
#         default=0,
#         db_index=True
#     )
#
#     create_date = models.DateTimeField(
#         verbose_name='Дата создания',
#         auto_now_add=True,
#         db_index=True
#     )
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = 'Журнал',
#         verbose_name_plural = 'Журналы'
#
#
# class SearchQuerySubscriber(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     journal = models.ForeignKey(SearchQuerySubscribe, on_delete=models.CASCADE)
#     create_date = models.DateTimeField(
#         verbose_name='Дата создания',
#         auto_now_add=True,
#         db_index=True
#     )
#
#     def __str__(self):
#         return '{user} - {journal}'.format(user=str(self.user), journal=str(self.journal))
#
#     class Meta:
#         verbose_name = 'Подписчик на журнал'
#         verbose_name_plural = 'Подписчики на журнал'
#         ordering = ['ordering', 'name']
#         unique_together = [('user', 'journal')]


"""
@receiver(pre_save, sender=User)
def user_post_save(sender, **kwargs):
    user = kwargs['instance']
    email = user.email
    if email:
        subscribers = Subscriber.objects.filter(user=user)
        for subscriber in subscribers:
            updated = False
            if subscriber.email != email:
                subscriber.email = email
                updated = True

            if user.is_active != subscriber.is_active:
                subscriber.is_active = user.is_active
                updated = True

            if updated:
                subscriber.save()
"""


# @receiver(pre_delete, sender=Subscriber)
# def subscriber_post_save(sender, **kwargs):
#     subscriber = kwargs['instance']
#     SubscribingLog(
#         subscribe = subscriber.subscribe,
#         user=subscriber.user,
#         action=SUBSCRIBING_LOG_ACTIONS['unsubscribe'],
#     ).save()

# class SubscribeState(models.Model):
# subscribe_type = models.ForeignKey(S)
# last_letter_datetime = models.DateTimeField(verbose_name=u'Дата формирования последнего письма', db_index=True)
#     class Meta:
#         verbose_name = u'Форимрование последнего письма рассылки'
#         verbose_name_plural = u'Статусы отправки писем'
#         unique_together = ('subscriber', 'letter')


def generate_key(subscriber_id, email):
    return hashlib.md5(('%s%s%s' % (SECRET_KEY, subscriber_id, email)).encode('utf-8')).hexdigest()


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


def _send_letter(letter):
    if not letter.broadcast:
        subscribers = Subscriber.objects.select_related('user').filter(
            subscribe=letter.subscribe_id,
            is_active=True
        )
        send_statuses = []

        for subscriber in subscribers.iterator():
            if len(send_statuses) > 20:
                SendStatus.objects.bulk_create(send_statuses)
                send_statuses = []
            if not SendStatus.objects.filter(subscriber=subscriber, letter=letter).exists():
                send_status = SendStatus(subscriber=subscriber, letter=letter)
                send_statuses.append(send_status)

        SendStatus.objects.bulk_create(send_statuses)
    else:
        users = User.objects.filter(
            is_active=True
        )
        send_statuses = []

        for user in users.iterator():
            if len(send_statuses) > 20:
                SendStatus.objects.bulk_create(send_statuses)
                send_statuses = []
            if not SendStatus.objects.filter(user=user, letter=letter).exists():
                if user.email:
                    send_status = SendStatus(user=user, letter=letter)
                    send_statuses.append(send_status)

        if send_statuses:
            SendStatus.objects.bulk_create(send_statuses)
    return True


@transaction.atomic()
def send_letters():
    now = timezone.now()
    letters = Letter.objects.filter(must_send_at__lte=now, send_completed=False)
    for letter in letters:
        sended = _send_letter(letter)
        if sended:
            letter.send_completed = True
            letter.save()


@transaction.atomic()
def send_to_email():
    send_statuses = SendStatus.objects.select_related('subscriber', 'user', 'letter').filter(is_sent=False)
    for send_status in send_statuses.iterator():

        user = None
        email = ''
        if send_status.subscriber:
            user = send_status.subscriber.user
            email = send_status.subscriber.email
        elif send_status.user:
            user = send_status.user
            email = send_status.user.email

        subscriber_parts = []

        if user:
            if user.last_name:
                subscriber_parts.append(user.last_name)
            if user.first_name:
                subscriber_parts.append(user.first_name)
        if not subscriber_parts:
            subscriber_parts.append(email)

        content_template = Template(send_status.letter.content)
        content = content_template.render(Context({
            'subscriber': ' '.join(subscriber_parts),
        }))

        key = ''
        if send_status.subscriber:
            key = generate_key(send_status.subscriber_id, send_status.subscriber.email)
        email_body = letter_template.render({
            'title': send_status.letter.subject,
            'content': content,
            'email': email,
            'key': key,
            'subscribe_id': send_status.letter.subscribe_id,
            'SITE_DOMAIN': SITE_DOMAIN
        })

        soup = bs4.BeautifulSoup(email_body, features='lxml')
        journal_redirect = 'https://' + SITE_DOMAIN + resolve_url('journal:redirect_to_url')

        for link in soup.find_all('a'):
            href = link['href']
            if href.startswith('mailto:') or href.startswith('tel:'):
                continue

            link['href'] = journal_redirect + '?u={href}&a=subscribe_click&attr_subscribe={subscribe_id}'.format(
                href=quote(link['href']),
                subscribe_id=str(send_status.letter.subscribe_id)
            )

        for img in soup.find_all('img'):
            src = img['src']
            if src.startswith('/static/') or src.startswith('/media/'):
                img['src'] = 'https://' + SITE_DOMAIN + img['src']

        email_body = str(soup.prettify(formatter=None))
        message = EmailMessage(
            subject=send_status.letter.subject,
            body=email_body,
            # from_email=SUBSCRIBE_FROM_EMAIL,
            to=[email],
            # connection=get_connection(EMAIL_BACKEND)
        )
        if send_status.letter.content_format == 'html':
            message.content_subtype = "html"

        try:
            message.send(fail_silently=False)
            send_status.is_sent = True
            send_status.save()
        except Exception as e:
            send_status.has_error = True
            send_status.error_message = str(e)
            send_status.save()


def clear_statuses():
    now = timezone.now()
    before_td = timezone.timedelta(days=3)
    before = now - before_td
    SendStatus.objects.filter(create_date__lte=before).delete()


def log_subscribing(user, subscribe, action=SUBSCRIBING_LOG_ACTIONS['subscribe']):
    """
    Журналирование процесса подписки
    """
    SubscribingLog.objects.bulk_create([SubscribingLog(subscribe=subscribe, user=user, action=action)])
