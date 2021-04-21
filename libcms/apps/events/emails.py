from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import resolve_url

from events.models import Event

SITE_DOMAIN = settings.SITE_DOMAIN
DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


def send_to_user_particinat_notification(event, user):
    if not user.email:
        return

    subject = 'Регистрация на мероприятие'
    message = [
        'Вы зарегистрировались на мероприятие "{event_title}".'.format(
            event_title=event.event_content.title,
        ),
        'Для просмотра информации о мероприятии перейдите по адресу {url}'.format(
            url=_get_event_url(event)
        )
    ]

    send_mail(
        subject=subject,
        message='\n'.join(message),
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )


def _get_event_url(event: Event):
    return 'https://' + SITE_DOMAIN + '' + resolve_url(
        'events:frontend:show',
        id=event.id
    )
