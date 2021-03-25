# coding=utf-8
import os
import subprocess
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, Http404
from guardian.decorators import permission_required_or_403
from .. import models
from . import forms
from .. import settings
DATE_RANGE_FORM_PREFIX = 'drf'


@login_required
def index(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    return render(request, 'subscribe/administration/index.html', {

    })


def groups(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    group_list = models.Group.objects.all()
    return render(request, 'subscribe/administration/groups.html', {
        'group_list': group_list
    })


@login_required
@permission_required_or_403('subscribe.add_group')
@transaction.atomic()
def create_group(request):
    if request.method == 'POST':
        form = forms.GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:groups')
    else:
        form = forms.GroupForm()

    return render(request, 'subscribe/administration/group_form.html', {
        'form': form
    })


@login_required
@permission_required_or_403('subscribe.change_group')
@transaction.atomic()
def change_group(request, id):
    group = get_object_or_404(models.Group, id=id)
    if request.method == 'POST':
        form = forms.GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:groups')
    else:
        form = forms.GroupForm(instance=group)

    return render(request, 'subscribe/administration/group_form.html', {
        'form': form,
        'group': group,
    })


@login_required
@permission_required_or_403('subscribe.delete_group')
@transaction.atomic()
def delete_group(request, id):
    group = get_object_or_404(models.Group, id=id)
    group.delete()
    return redirect('subscribe:administration:groups')


@login_required
@transaction.atomic()
def subscribes(request, group_id=None):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')

    q = Q()
    if group_id:
        q &= Q(group_id=group_id)

    subscribe_list = models.Subscribe.objects.filter(q)
    paginator = Paginator(subscribe_list, 25)
    page = request.GET.get('page')
    subscribes_page = paginator.get_page(page)
    groups = models.Group.objects.all().order_by('order')

    return render(request, 'subscribe/administration/subscribes.html', {
        'subscribes_page': subscribes_page,
        'groups': groups,
        'group_id': group_id,
    })


@login_required
@permission_required_or_403('subscribe.add_subscribe')
@transaction.atomic()
def create_subscribe(request):
    if request.method == 'POST':
        form = forms.SubscribeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:subscribes')
    else:
        form = forms.SubscribeForm()

    return render(request, 'subscribe/administration/subscribe_form.html', {
        'form': form
    })


@login_required
@permission_required_or_403('subscribe.change_subscribe')
@transaction.atomic()
def change_subscribe(request, id):
    subscribe = get_object_or_404(models.Subscribe, id=id)
    if request.method == 'POST':
        form = forms.SubscribeForm(request.POST, instance=subscribe)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:subscribes')
    else:
        form = forms.SubscribeForm(instance=subscribe)

    return render(request, 'subscribe/administration/subscribe_form.html', {
        'form': form,
        'subscribe': subscribe,
    })


@login_required
@permission_required_or_403('subscribe.delete_subscribe')
@transaction.atomic()
def delete_subscribe(request, id):
    subscribe = get_object_or_404(models.Subscribe, id=id)
    subscribe.delete()
    return redirect('subscribe:administration:subscribes')


@login_required
@transaction.atomic()
def letters(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    letter_list = models.Letter.objects.select_related('subscribe').all()
    paginator = Paginator(letter_list, 25)
    page = request.GET.get('page')
    letters_page = paginator.get_page(page)
    return render(request, 'subscribe/administration/letters.html', {
        'letters_page': letters_page
    })


@login_required
@permission_required_or_403('subscribe.add_letter')
@transaction.atomic()
def create_letter(request):
    if request.method == 'POST':
        form = forms.LetterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:letters')
    else:
        form = forms.LetterForm()

    return render(request, 'subscribe/administration/letter_form.html', {
        'form': form
    })


@login_required
@permission_required_or_403('subscribe.change_letter')
@transaction.atomic()
def change_letter(request, id):
    letter = get_object_or_404(models.Letter, id=id)
    if request.method == 'POST':
        form = forms.LetterForm(request.POST, instance=letter)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:letters')
    else:
        form = forms.LetterForm(instance=letter)

    return render(request, 'subscribe/administration/letter_form.html', {
        'form': form,
        'letter': letter,
    })


@login_required
@permission_required_or_403('subscribe.delete_letter')
@transaction.atomic()
def delete_letter(request, id):
    letter = get_object_or_404(models.Letter, id=id)
    letter.delete()
    return redirect('subscribe:administration:letters')


@login_required
def send_letters(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    models.send_letters()
    models.send_to_email()
    models.clear_statuses()
    return redirect('subscribe:administration:letters')


@login_required
@transaction.atomic()
def subscribers(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    filter = request.GET.get('filter')
    q = Q()
    if filter:
        q &= Q(user__email__icontains=filter)
    subscriber_list = models.Subscriber.objects.filter(q)
    paginator = Paginator(subscriber_list, 25)
    page = request.GET.get('page')
    subscribers_page = paginator.get_page(page)
    return render(request, 'subscribe/administration/subscribers.html', {
        'subscribers_page': subscribers_page
    })


@login_required
@permission_required_or_403('subscriber.add_subscriber')
@transaction.atomic()
def create_subscriber(request):
    if request.method == 'POST':
        form = forms.SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:subscribers')
    else:
        form = forms.SubscriberForm()

    return render(request, 'subscribe/administration/subscriber_form.html', {
        'form': form
    })


@login_required
@permission_required_or_403('subscribe.change_subscriber')
@transaction.atomic()
def change_subscriber(request, id):
    subscriber = get_object_or_404(models.Subscriber, id=id)
    if request.method == 'POST':
        form = forms.SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            form.save()
            return redirect('subscribe:administration:subscribers')
    else:
        form = forms.SubscriberForm(instance=subscriber)

    return render(request, 'subscribe/administration/subscriber_form.html', {
        'form': form,
        'subscriber': subscriber,
    })


@login_required
@permission_required_or_403('subscribe.delete_subscriber')
@transaction.atomic()
def delete_subscriber(request, id):
    subscriber = get_object_or_404(models.Subscriber, id=id)
    subscriber.delete()
    return redirect('subscribe:administration:subscribers')


@login_required
@transaction.atomic()
def send_statuses(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    send_status_list = models.SendStatus.objects.select_related('subscriber', 'subscriber__user', 'letter',
                                                                'letter__subscribe').all()
    paginator = Paginator(send_status_list, 25)
    page = request.GET.get('page')
    send_statuses_page = paginator.get_page(page)
    return render(request, 'subscribe/administration/send_statuses.html', {
        'send_statuses_page': send_statuses_page
    })


@login_required
@permission_required_or_403('subscribe.delete_sendstatus')
@transaction.atomic()
def delete_send_status(request, id):
    send_status = get_object_or_404(models.SendStatus, id=id)
    send_status.delete()
    return redirect('subscribe:administration:send_statuses')


@login_required
@permission_required_or_403('subscribe.delete_sendstatus')
@transaction.atomic()
def delete_all_send_statuses(request):
    send_statuses = models.SendStatus.objects.all()
    send_statuses._raw_delete(send_statuses.db)
    return redirect('subscribe:administration:send_statuses')


@login_required
def statistics(request):
    if not request.user.has_module_perms('subscribe'):
        return HttpResponseForbidden('Нет прав для доступа')
    now = datetime.now()
    DateRangeForm = forms.get_date_range_form(
        init_start_date=now,
        init_end_date=now
    )

    if request.GET.get('filter'):
        date_range_form = DateRangeForm(request.GET, prefix=DATE_RANGE_FORM_PREFIX)
    else:
        date_range_form = DateRangeForm(prefix=DATE_RANGE_FORM_PREFIX)

    filter_params = _get_filter_params(request, date_range_form)
    user_group = filter_params.get('user_group')

    q = Q(create_date__gte=filter_params['start_date'], create_date__lt=filter_params['end_date'])

    if user_group:
        q &= Q(user__groups__in=[user_group])
    subscribing_log_queryset = models.SubscribingLog.objects.filter(q)

    total_user_by_action = {}
    group_by_subscribes = {}

    for subscribing_log in subscribing_log_queryset.iterator():
        group_by_subscribes = _group_by_subscribes(group_by_subscribes, subscribing_log)
        total_user_by_action = _total_user_by_action(total_user_by_action, subscribing_log)

    return render(request, 'subscribe/administration/statistics.html', {
        'summary_parameters': _get_summary_parameters(),
        'range_form': date_range_form,
        'total_user_by_action': _render_total_user_by_action(total_user_by_action),
        'group_by_subscribes': _render_group_by_subscribes(group_by_subscribes),
        'subscribes_popularity': _get_subscribes_popularity(),
        'start_date': filter_params['start_date'],
        'end_date': filter_params['end_date'],
    })


@login_required
@transaction.atomic()
def commands(request):
    if not request.user.has_module_perms('subscribe'):
       return HttpResponseForbidden('Нет прав для доступа')

    commands = settings.COMMANDS
    return render(request, 'subscribe/administration/commands.html', {
        'commands': commands,
    })


@login_required
@transaction.atomic()
def run_command(request, index):
    if not request.user.has_module_perms('subscribe'):
       return HttpResponseForbidden('Нет прав для доступа')
    int_index = int(index)
    commands = settings.COMMANDS[int_index:int_index + 1]
    if not commands:
        raise Http404('Command not found')
    command = commands[0]['command']
    print(settings.MANAGE_PY_PATH)
    print(settings.PYTHON_PATH)
    print(command)
    cmd = '""%s" "%s" %s"' % (settings.PYTHON_PATH, settings.MANAGE_PY_PATH, command, )
    print(cmd)
    os.system(cmd)
    """try:
        out = subprocess.check_output([settings.PYTHON_PATH, settings.MANAGE_PY_PATH] + command.split())
    except subprocess.CalledProcessError as e:
        out = str(e.output)  
    print(out)
    """ 
    return redirect('subscribe:administration:commands')


def _render_group_by_subscribes(group_by_subscribes):
    actions_title = models.get_actions_title()
    subscribes_title = models.get_subscribe_titles(list(group_by_subscribes.keys()))

    report_lines = []

    for subscribe_id, actions in list(group_by_subscribes.items()):
        report_line = {
            'id': subscribe_id,
            'title': subscribes_title.get(subscribe_id, subscribe_id),
            'actions': []
        }

        for action_id, user_set in list(actions.items()):
            report_line['actions'].append({
                'id': action_id,
                'title': actions_title.get(action_id, action_id),
                'value': len(user_set)
            })

        report_lines.append(report_line)
    return report_lines


def _render_total_user_by_action(total_user_by_action):
    actions_title = models.get_actions_title()
    total_user_by_action_list = []
    for action, users_subscribe_set in list(total_user_by_action.items()):
        total_user_by_action_list.append({
            'id': action,
            'title': actions_title.get(action, action),
            'value': len(users_subscribe_set)
        })
    return total_user_by_action_list


def _get_subscribes_popularity():
    def _subscribes_popularity(subscribes_popularity, subscriber):
        subscriber_subscribes = subscriber.subscribe.all().values('id')
        for subscriber_subscribe in subscriber_subscribes:
            subscribe_id = subscriber_subscribe.get('id')
            user_count = subscribes_popularity.get(subscribe_id, 0)
            subscribes_popularity[subscribe_id] = user_count + 1
        return subscribes_popularity

    subscribes_popularity = {}
    subscribe_titles = {}

    for subscribe in models.Subscribe.objects.all().values('id', 'name'):
        subscribes_popularity[subscribe.get('id')] = 0
        subscribe_titles[subscribe.get('id')] = subscribe.get('name')

    all_subscribers_queryset = models.Subscriber.objects.prefetch_related('subscribe').all()
    for subscriber in all_subscribers_queryset.iterator():
        subscribes_popularity = _subscribes_popularity(subscribes_popularity, subscriber)

    subscribes_popularity_list = []
    for sibscribe_id, count in list(subscribes_popularity.items()):
        subscribes_popularity_list.append({
            'id': sibscribe_id,
            'value': count,
            'title': subscribe_titles.get(sibscribe_id, '')
        })
    subscribes_popularity_list.sort(key=lambda x: x['value'], reverse=True)
    return subscribes_popularity_list


def _group_by_subscribes(subscribes, subscribing_log):
    """
    subscribes = {
        'subscribe_id': {
            'action_id': set('user_id')
        }
    }
    """
    subscribe = subscribes.get(subscribing_log.subscribe_id, {})
    if not subscribe:
        subscribes[subscribing_log.subscribe_id] = subscribe

    subscribe_action = subscribe.get(subscribing_log.action, set())
    if not subscribe_action:
        subscribe[subscribing_log.action] = subscribe_action

    subscribe_action.add(subscribing_log.user_id)
    return subscribes


def _total_user_by_action(total_user_by_action, subscribing_log):
    """
    total_user_by_action = {
        'action_id': set('user_id + subscribe_id')
    }
    """
    action_user_subscribe = total_user_by_action.get(subscribing_log.action, set())

    if not action_user_subscribe:
        total_user_by_action[subscribing_log.action] = action_user_subscribe

    action_user_subscribe.add('%s:%s' % (subscribing_log.user_id, subscribing_log.subscribe_id))
    return total_user_by_action


def _get_summary_parameters():
    summary_parameters = [
        {
            'title': 'Количество подписчиков',
            'value': models.Subscriber.objects.all().count()
        },
        {
            'title': 'Количество подписок',
            'value': models.Subscribe.objects.all().count()
        },
    ]
    return summary_parameters


def _get_filter_params(request, date_range_form):
    def end_of_day(dt):
        return datetime(year=dt.year, month=dt.month, day=dt.day, hour=23, minute=59, second=59)

    now = datetime.now()
    start_date = datetime(year=now.year, month=now.month, day=now.day)
    end_date = end_of_day(now)
    user_group = None
    # group = 'D'

    if date_range_form.is_valid():
        start_date = date_range_form.cleaned_data['start_date'] or start_date
        end_date = date_range_form.cleaned_data['end_date'] or end_date
        end_date = end_of_day(end_date)
        user_group = date_range_form.cleaned_data.get('user_group')
        # group = date_range_form.cleaned_data['group'] or group

    return {
        'start_date': start_date,
        'end_date': end_date,
        'user_group': user_group,
        # 'group': group
    }
