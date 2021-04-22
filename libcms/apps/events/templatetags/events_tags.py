# -*- coding: utf-8 -*-
from datetime import date, datetime
from django.utils import timezone
import calendar
from django.db.models import Q
from django import template
from django.core.cache import cache

from ..constants import ONLINE_ADDRESS_REFERENCE_ID
from ..models import Event
from ..frontend.forms import CalendarFilterForm, get_current_month_choice, get_current_year_choice
from ..frontend.views import _join_content
register = template.Library()


@register.inclusion_tag('events/tags/events_calendar.html', takes_context=True)
def events_calendar(context, y=0, m=0):
    request = context['request']

    if request.method == 'POST':
        form = CalendarFilterForm(request.POST)
        if form.is_valid():
            y = int(form.cleaned_data['year'])
            m = int(form.cleaned_data['month'])
    else:
        form = CalendarFilterForm(initial={'month': get_current_month_choice(),
                                           'year': get_current_year_choice()})
    today = date.today()
    year = today.year
    month = today.month

    if y: year = y
    if m: month = m

    cache_key = 'events_y_m' + str(year) + str(month) + 'active=1'

    month_range = calendar.monthrange(year, month)
    start = timezone.datetime(year, month, 1, 0, 0, 0)
    end = timezone.datetime(year, month, month_range[1], 0, 0, 0)
    q = Q(active=True) & Q(Q(start_date__lte=start) | Q(start_date__lte=end)) & Q(end_date__gte=start)
    # events = Event.objects.filter(active=True, start_date__lte=start, end_date__gte=end)
    events = Event.objects.filter(q).values('id', 'start_date', 'end_date')
    # if not events:
    #     events = list(events)
    #     cache.set(cache_key, events)

    calendar_of_events = []

    weeks = calendar.monthcalendar(year, month)
    for week in weeks:
        week_events = []
        for day in week:
            day_events = {'day': day, 'today': False, 'events': []}
            if day == today.day and year == today.year and month == today.month:
                day_events['today'] = True
            for event in events:
                if day == 0: continue
                date_for_day_start = timezone.datetime(year, month, day, 0, 0, 0)
                date_for_day_end = timezone.datetime(year, month, day, 23, 59, 59)
                if (event['start_date'] <= date_for_day_start or event['start_date'] <= date_for_day_end) and event[
                    'end_date'] >= date_for_day_start:
                    day_events['events'].append({
                        'id': event['id'],
                        #                        'title': event.title,
                        #                        'teaser': event.teaser
                    })
            week_events.append(day_events)
        calendar_of_events.append(week_events)
    return {
        'calendar': calendar_of_events,
        'month': month,
        'year': year,
        'form': form
    }


@register.inclusion_tag('events/tags/broadcasts.html', takes_context=True)
def events_broadcasts(context):
    now = timezone.now()
    q = Q(address_reference=ONLINE_ADDRESS_REFERENCE_ID)
    q &= Q(start_date__gte=now) | Q(start_date__lte=now, end_date__gte=now)
    events = Event.objects.filter(q).order_by('start_date')[:4]
    _join_content(events)
    return {
        'events': events,
        'now': now
    }
