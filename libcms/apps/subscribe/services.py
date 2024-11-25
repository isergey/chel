# encoding: utf-8
import hashlib
from base64 import urlsafe_b64encode
from urllib.parse import quote

import bs4
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import transaction
from django.shortcuts import resolve_url
from django.template import Context, Template
from django.template.loader import get_template
from django.utils import timezone
from django.conf import settings

from subscribe.models import SendStatus, Subscriber, Letter, SUBSCRIBING_LOG_ACTIONS, SubscribingLog

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SUBSCRIBE_FROM_EMAIL = getattr(settings, 'SUBSCRIBE_FROM_EMAIL', 'subscribe@localhost')
SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost')
SECRET_KEY = getattr(settings, 'SECRET_KEY', '')

letter_template = get_template('subscribe/letter/base.html')


@transaction.atomic()
def send_letters():
    now = timezone.now()
    letters = Letter.objects.select_for_update().filter(must_send_at__lte=now, send_completed=False)
    for letter in letters:
        sent = __send_letter(letter)
        if sent:
            letter.send_completed = True
            letter.save()


@transaction.atomic()
def send_to_email():
    send_statuses = SendStatus.objects.select_for_update().select_related('subscriber', 'user', 'letter').filter(is_sent=False)
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
            key = __generate_key(send_status.subscriber_id, send_status.subscriber.email)
        email_body = letter_template.render({
            'title': send_status.letter.subject,
            'content': content,
            'email': email,
            'key': key,
            'subscribe_id': send_status.letter.subscribe_id,
            'SITE_DOMAIN': SITE_DOMAIN
        })
        soup = bs4.BeautifulSoup(email_body, features='lxml')

        unsubscribe_link = soup.find(id='unsubscribe_link')

        if unsubscribe_link:
            unsubscribe_link['href'] = 'https://' + SITE_DOMAIN + resolve_url(
                'subscribe:frontend:index') + '?email={email}&key={key}'.format(
                email=email,
                key=key
            )

        journal_redirect = 'https://' + SITE_DOMAIN + resolve_url('journal:redirect_to_url')

        for link in soup.find_all('a'):
            href = link['href']
            if href.startswith('mailto:') or href.startswith('tel:'):
                continue

            link['href'] = journal_redirect + '?u={href}&a=subscribe_click&attr_subscribe={subscribe_id}'.format(
                href=urlsafe_b64encode(quote(link['href']).encode('utf-8')).decode('utf-8'),
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


@transaction.atomic()
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


def __send_letter(letter):
    if letter.to_subscriber is not None:
        if not SendStatus.objects.filter(letter=letter).exists():
            SendStatus.objects.bulk_create([SendStatus(subscriber=letter.to_subscriber, letter=letter)])
    elif not letter.broadcast:
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


def __generate_key(subscriber_id, email):
    return hashlib.md5(('%s%s%s' % (SECRET_KEY, subscriber_id, email)).encode('utf-8')).hexdigest()
