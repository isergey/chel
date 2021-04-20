# -*- coding: utf-8 -*-
import datetime
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.utils import translation
from django.utils.translation import get_language

from common.pagination import get_page
from opac_global_client.entities import ReaderResponse

from . import forms
from .. import models
from ..models import Address
from sso import models as sso_models
from sso_opac.settings import AUTH_SOURCE as OPAC_AUTH_SOURCE


def index(request):
    q = Q(active=True)

    filter_form = forms.EventsFilterForm(request.GET)
    start_date = None
    end_date = None
    if filter_form.is_valid():
        keywords = filter_form.cleaned_data['keywords']
        if keywords:
            q &= Q(keywords__icontains=keywords)

        start_date = filter_form.cleaned_data['start_date']
        if start_date is not None:
            start_date_q = Q(start_date__gte=datetime.datetime(
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
                hour=0,
                minute=0,
                second=0
            ))

            start_date_q |= Q(Q(start_date__lte=datetime.datetime(
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
                hour=0,
                minute=0,
                second=0
            )) & Q(end_date__gte=datetime.datetime(
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
                hour=0,
                minute=0,
                second=0
            )))

            q &= start_date_q

        end_date = filter_form.cleaned_data['end_date']

        if end_date is not None:
            end_date_q = Q(end_date__lte=datetime.datetime(
                year=end_date.year,
                month=end_date.month,
                day=end_date.day,
                hour=23,
                minute=59,
                second=59
            ))

            end_date_q |= Q(Q(start_date__lte=datetime.datetime(
                year=end_date.year,
                month=end_date.month,
                day=end_date.day,
                hour=0,
                minute=0,
                second=0
            )) & Q(end_date__gte=datetime.datetime(
                year=end_date.year,
                month=end_date.month,
                day=end_date.day,
                hour=23,
                minute=59,
                second=59
            )))

            q &= end_date_q


        category = filter_form.cleaned_data['category']
        if category:
            q &= Q(category__in=category)

        # age_category = filter_form.cleaned_data['age_category']
        # if age_category:
        #     q &= Q(age_category__gte=age_category)

        address: Address = filter_form.cleaned_data['address']
        if address:
            q &= Q(address_reference__in=address.get_descendants(include_self=True))

    events_qs = models.Event.objects.filter(q).order_by('start_date')

    if not start_date and not end_date:
        events_qs = events_qs.exclude(end_date__lte=datetime.datetime.now())

    events_page = get_page(request, events_qs)

    event_contents = list(models.EventContent.objects.filter(
        event__in=list(events_page.object_list),
        lang=get_language()[:2]
    ))

    t_dict = {}
    for event in events_page.object_list:
        t_dict[event.id] = {'event': event}

    for event_content in event_contents:
        t_dict[event_content.event_id]['event'].event_content = event_content

    return render(request, 'events/frontend/list.html', {
        'events_list': events_page.object_list,
        'events_page': events_page,
        'filter_form': filter_form
    })


def filer_by_date(request, year='', month='', day=''):
    if int(month) < 10:
        month = '0' + month

    if int(day) < 10:
        day = '0' + day

    return redirect(resolve_url('events:frontend:index') + '?start_date={start_date}&end_date={end_date}'.format(
        start_date='{year}-{month}-{day}'.format(year=year, month=month, day=day),
        end_date='{year}-{month}-{day}'.format(year=year, month=month, day=day),
    ))

    # start_date = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=0, minute=0, second=0)
    # events_page = get_page(request, Event.objects.filter(active=True, start_date__lte=start_date, end_date__gte=start_date).order_by('-create_date'))

    day_datetime = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
    end_day_datetime = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
    q = Q(active=True) & Q(start_date__lte=end_day_datetime) & Q(end_date__gte=day_datetime)
    events_page = get_page(request, models.Event.objects.filter(q).order_by('-start_date'))
    event_contents = list(
        models.EventContent.objects.filter(event__in=list(events_page.object_list), lang=get_language()[:2]))

    t_dict = {}
    for event in events_page.object_list:
        t_dict[event.id] = {'event': event}

    for event_content in event_contents:
        t_dict[event_content.event_id]['event'].event_content = event_content
    return render(request, 'events/frontend/list.html', {
        'events_list': events_page.object_list,
        'events_page': events_page,
        'start_date': day_datetime

    })


def show(request, id):
    cur_language = translation.get_language()
    event = get_object_or_404(models.Event, id=id)
    try:
        content = models.EventContent.objects.get(event=event, lang=cur_language[:2])
    except models.EventContent.DoesNotExist:
        content = None

    participant = None
    if request.user.is_authenticated:
        participant = models.EventParticipant.objects.filter(event=event, user=request.user).first()
    return render(request, 'events/frontend/show.html', {
        'event': event,
        'content': content,
        'participant': participant
    })


@login_required
@atomic
def favorit_events(request):
    fav_events_page = get_page(request, models.EventParticipant.objects.filter(user=request.user))
    events = []
    for fav_event in fav_events_page.object_list:
        events.append(fav_event.event_id)

    events = models.Event.objects.filter(id__in=events)
    event_contents = list(models.EventContent.objects.filter(event__in=list(events), lang=get_language()[:2]))

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
@atomic
def add_to_favorits(request, id):
    event = get_object_or_404(models.Event, id=id)
    try:
        favorite_event = models.FavoriteEvent.objects.get(user=request.user, event=event)
    except models.FavoriteEvent.DoesNotExist:
        models.FavoriteEvent(user=request.user, event=event).save()
    return redirect('events:frontend:favorit_events')


@login_required
@atomic
def favorite_show(request, id):
    cur_language = translation.get_language()
    event = get_object_or_404(models.Event, id=id)
    try:
        content = models.EventContent.objects.get(event=event, lang=cur_language[:2])
    except models.EventContent.DoesNotExist:
        content = None

    return render(request, 'events/frontend/favorite_show.html', {
        'event': event,
        'content': content
    })


@login_required
@atomic
def delete_from_favorite(request, id):
    event = get_object_or_404(models.Event, id=id)
    try:
        favorite_event = models.FavoriteEvent.objects.get(user=request.user, event=event)
        favorite_event.delete()
    except models.FavoriteEvent.DoesNotExist:
        models.FavoriteEvent(user=request.user, event=event).save()
    return redirect('events:frontend:favorit_events')


@login_required
@atomic
def participant(request, id):
    event = get_object_or_404(models.Event, id=id)
    cur_language = translation.get_language()
    content = models.EventContent.objects.filter(event=event, lang=cur_language[:2]).first()

    if request.method == 'POST':
        form = forms.ParticipantForm(request.POST)
        if form.is_valid():
            participant = models.EventParticipant(
                user=request.user,
                event=event,
                last_name=form.cleaned_data['last_name'],
                first_name=form.cleaned_data['first_name'],
                reader_id=form.cleaned_data['reader_id'],
                email=form.cleaned_data['email'],
            )
            participant.save()
            return redirect('events:frontend:show', id=id)

    else:
        external_user = sso_models.get_external_users(request.user, auth_source=OPAC_AUTH_SOURCE)
        reader_id = ''
        if external_user:
            response = ReaderResponse(**external_user.get_attributes())
            reader_id = response.attributes.barcode or ''

        form = forms.ParticipantForm(initial={
            'last_name': request.user.last_name,
            'first_name': request.user.first_name,
            'email': request.user.email,
            'reader_id': reader_id,
        })

    return render(request, 'events/frontend/participant.html', {
        'event': event,
        'content': content,
        'form': form,
    })


@login_required
@atomic
def delete_participant(request, id):
    event = get_object_or_404(models.Event, id=id)
    participant = models.EventParticipant.objects.filter(event=event, user=request.user).first()
    if participant is not None:
        participant.delete()
    return redirect('events:frontend:show', id=id)



