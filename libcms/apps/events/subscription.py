from typing import List, Optional
from django.conf import settings
from django.template.loader import render_to_string

from subscribe.models import Subscribe, Letter
from .models import Event

SUBSCRIPTION_CODE = 'events'

SITE_DOMAIN = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')


def create_subscription_letter(event_list: List[Event]) -> Optional[Letter]:
    if not len(event_list):
        return

    subscribe = Subscribe.objects.filter(code=SUBSCRIPTION_CODE).first()

    if subscribe is None:
        subscribe = Subscribe(
            code=SUBSCRIPTION_CODE,
            name='События'
        )
        subscribe.save()

    content = render_to_string('events/email/subscription.html', {
        'event_list': event_list,
        'subscribe': subscribe,
        'SITE_DOMAIN': SITE_DOMAIN
    })

    letter = Letter(
        subscribe=subscribe,
        subject='События',
        content_format='html',
        content=content
    )

    letter.save()
    return letter