# -*- coding: utf-8 -*-
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required
from django.utils.translation import get_language

from common.pagination import get_page
from ..models import Event, EventContent, EventParticipant
from .forms import EventForm, EventContentForm, EventFilterForm


@login_required
@permission_required_or_403('events.add_event')
def index(request):
    if not request.user.has_module_perms('events'):
        return HttpResponseForbidden()
    return redirect('events:administration:events_list')


@login_required
def events_list(request):
    now = timezone.now()
    if not request.user.has_module_perms('events'):
        return HttpResponseForbidden()
    if request.GET.get('filter', '') == 'on':
        filter_form = EventFilterForm(request.GET)
    else:
        filter_form = EventFilterForm()

    sorting = 'create_date'
    order = '-'
    q = Q()

    if request.GET.get('filter', '') == 'on':
        if filter_form.is_valid():
            filter_sort = filter_form.cleaned_data['sort']

            if filter_sort:
                sorting = filter_sort

            filter_order = filter_form.cleaned_data['order']

            if filter_order:
                if filter_order == 'asc':
                    order = ''
                elif filter_order == 'desc':
                    order = '-'

            filter_active = filter_form.cleaned_data['active']
            q &= Q(active=bool(filter_active))

            filter_ended = filter_form.cleaned_data['ended']

            if filter_ended:
                q &= Q(end_date__lt=now)

            filter_start_date = filter_form.cleaned_data['start_date']
            filter_end_date = filter_form.cleaned_data['end_date']

            if filter_start_date:
                q &= Q(start_date__gte=filter_start_date)

            if filter_end_date:
                q &= Q(end_date__lte=filter_end_date)

    events_page = get_page(request, Event.objects.filter(q).order_by(order + sorting), 10)

    event_contents = list(EventContent.objects.filter(event__in=list(events_page.object_list), lang=get_language()[:2]))

    t_dict = {}
    for event in events_page.object_list:
        t_dict[event.id] = {'event': event}

    for event_content in event_contents:
        t_dict[event_content.event_id]['event'].event_content = event_content

    return render(request, 'events/administration/events_list.html', {
        'events_list': events_page.object_list,
        'events_page': events_page,
        'filter_form': filter_form
    })


@login_required
@permission_required_or_403('events.add_event')
@transaction.atomic()
def create_event(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, prefix='event_form')
        event_content_forms = []
        for lang in settings.LANGUAGES:
            event_content_forms.append({
                'form': EventContentForm(request.POST, prefix='event_content' + lang[0]),
                'lang': lang[0]
            })

        if event_form.is_valid():
            valid = False
            for event_content_form in event_content_forms:
                valid = event_content_form['form'].is_valid()
                if not valid:
                    break
            if valid:
                event = event_form.save(commit=False)
                event.save()
                event_form.save_m2m()
                for event_content_form in event_content_forms:
                    event_content = event_content_form['form'].save(commit=False)
                    event_content.lang = event_content_form['lang']
                    event_content.event = event
                    event_content.save()
                return redirect('events:administration:events_list')
    else:
        event_form = EventForm(prefix="event_form")
        event_content_forms = []
        for lang in settings.LANGUAGES:
            event_content_forms.append({
                'form': EventContentForm(prefix='event_content' + lang[0]),
                'lang': lang[0]
            })

    return render(request, 'events/administration/create_event.html', {
        'event_form': event_form,
        'event_content_forms': event_content_forms,
    })


@login_required
@permission_required_or_403('events.change_event')
@transaction.atomic()
def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
    event_contents = EventContent.objects.filter(event=event)
    event_contents_langs = {}

    for lang in settings.LANGUAGES:
        event_contents_langs[lang] = None

    for event_content in event_contents:
        event_contents_langs[event_content.lang] = event_content

    if request.method == 'POST':
        event_form = EventForm(request.POST, prefix='event_form', instance=event)

        if event_form.is_valid():
            event_form.save()
            event_content_forms = []
            for lang in settings.LANGUAGES:
                if lang in event_contents_langs:
                    lang = lang[0]
                    if lang in event_contents_langs:
                        event_content_forms.append({
                            'form': EventContentForm(request.POST, prefix='event_content_' + lang,
                                                     instance=event_contents_langs[lang]),
                            'lang': lang
                        })
                    else:
                        event_content_forms.append({
                            'form': EventContentForm(request.POST, prefix='event_content_' + lang),
                            'lang': lang
                        })

            valid = False
            for event_content_form in event_content_forms:
                valid = event_content_form['form'].is_valid()
                if not valid:
                    break

            if valid:
                for event_content_form in event_content_forms:
                    event_content = event_content_form['form'].save(commit=False)
                    event_content.event = event
                    event_content.lang = event_content_form['lang']
                    event_content.save()

                return redirect('events:administration:events_list')
    else:
        event_form = EventForm(prefix="event_form", instance=event)
        event_content_forms = []
        for lang in settings.LANGUAGES:
            lang = lang[0]
            if lang in event_contents_langs:
                event_content_forms.append({
                    'form': EventContentForm(prefix='event_content_' + lang, instance=event_contents_langs[lang]),
                    'lang': lang
                })
            else:
                event_content_forms.append({
                    'form': EventContentForm(prefix='event_content_' + lang),
                    'lang': lang
                })

    participants_count = EventParticipant.objects.filter(event=event).count()
    return render(request, 'events/administration/edit_event.html', {
        'event': event,
        'event_form': event_form,
        'event_content_forms': event_content_forms,
        'participants_count': participants_count,
    })


@login_required
@permission_required_or_403('events.delete_event')
@transaction.atomic()
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect('events:administration:events_list')


@login_required
@permission_required_or_403('events.add_event')
def participants(request, id):
    event = get_object_or_404(Event, id=id)
    content = EventContent.objects.filter(event=event).first()
    event_participants = EventParticipant.objects.filter(event=event)
    return render(request, 'events/administration/participants.html', {
        'event': event,
        'content': content,
        'participants': event_participants,
    })
