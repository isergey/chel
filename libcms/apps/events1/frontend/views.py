# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.utils.translation import get_language
from common.pagination import get_page
from ..models import Event, EventContent, FavoriteEvent


def index(request):
    events_page = get_page(request, Event.objects.filter(active=True).order_by('-create_date'))

    event_contents = list(EventContent.objects.filter(event__in=list(events_page.object_list), lang=get_language()[:2]))

    t_dict = {}
    for event in events_page.object_list:
        t_dict[event.id] = {'event': event}

    for event_content in event_contents:
        t_dict[event_content.event_id]['event'].event_content = event_content

    return render(request, 'events/frontend/list.html', {
        'events_list': events_page.object_list,
        'events_page': events_page,
        })

def filer_by_date(request, day='', month='', year=''):
    events_page = get_page(request, Event.objects.filter(active=True, start_date__year=year, start_date__month=month, start_date__day=day).order_by('-create_date'))
    event_contents = list(EventContent.objects.filter(event__in=list(events_page.object_list), lang=get_language()[:2]))

    t_dict = {}
    for event in events_page.object_list:
        t_dict[event.id] = {'event': event}

    for event_content in event_contents:
        t_dict[event_content.event_id]['event'].event_content = event_content
    return render(request, 'events/frontend/list.html', {
        'events_list': events_page.object_list,
        'events_page': events_page,

        })

def show(request, id):
    cur_language = translation.get_language()
    event = get_object_or_404(Event, id=id)
    try:
        content = EventContent.objects.get(event=event, lang=cur_language[:2])
    except EventContent.DoesNotExist:
        content = None

    return render(request, 'events/frontend/show.html', {
        'event': event,
        'content': content
    })

@login_required
def favorit_events(request):
    fav_events_page = get_page(request, FavoriteEvent.objects.filter(user=request.user))
    events = []
    for fav_event in fav_events_page.object_list:
        events.append(fav_event.event_id)

    events = Event.objects.filter(id__in=events)
    event_contents = list(EventContent.objects.filter(event__in=list(events), lang=get_language()[:2]))

    t_dict = {}
    for event in events:
        t_dict[event.id] = {'event': event}

    for event_content in event_contents:
        t_dict[event_content.event_id]['event'].event_content = event_content

    return render(request, 'events/frontend/favorites_list.html', {
        'events_list': events,
        'events_page': fav_events_page,
        })

@login_required
def add_to_favorits(request, id):
    event = get_object_or_404(Event, id=id)
    try:
        favorite_event = FavoriteEvent.objects.get(user=request.user, event=event)
    except FavoriteEvent.DoesNotExist:
        FavoriteEvent(user=request.user, event=event).save()
    return redirect('events:frontend:favorit_events')


def favorite_show(request, id):
    cur_language = translation.get_language()
    event = get_object_or_404(Event, id=id)
    try:
        content = EventContent.objects.get(event=event, lang=cur_language[:2])
    except EventContent.DoesNotExist:
        content = None

    return render(request, 'events/frontend/favorite_show.html', {
        'event': event,
        'content': content
    })