from datetime import datetime
from django.template.loader import render_to_string
from django.db.models import Q
from . import models

from subscribe.models import Subscribe, Letter


def generate_events_letter(q: Q, start_date: datetime.date):

    events = models.Event.objects.filter(q)

    content = render_to_string('events/letters/events.html', {
        'events': events
    })

    subscribe = Subscribe.objects.filter(code='events').first()

    if subscribe is None:
        subscribe = Subscribe(
            code='events',
            name='События'
        )
        subscribe.save()

    letter = Letter(
        subscribe=subscribe,
        subject='События ЧОУНБ за {from_date}'.format(from_date=str(start_date)),
        content_format='html',
        content=content
    )

    letter.save()




