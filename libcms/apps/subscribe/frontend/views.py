# encoding: utf-8
import json
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from common.pagination import get_page
from .. import models
from .forms import get_subscriber_form, EmailForm


@transaction.atomic()
def index(request):
    email = ''
    groups = models.Group.objects.filter(hidden=False)
    user = None
    if request.user.is_authenticated:
        email = request.user.email
        user = request.user
    # subscribes = Subscribe.objects.filter(is_active=True)
    if request.method == 'POST':
        email_form = EmailForm(request.POST)
        forms = []
        for group in groups:
            SubscriberForm = get_subscriber_form(
                models.Subscribe.objects.filter(group=group, is_active=True, hidden=False))
            forms.append({
                'group': group,
                'form': SubscriberForm(request.POST, prefix=group.id)
            })
        subscribes = []
        is_valid = True
        for form in forms:
            subscriber_form = form['form']
            if not subscriber_form.is_valid():
                is_valid = False
            else:
                subscribes += subscriber_form.cleaned_data['subscribes']

        if not email_form.is_valid():
            is_valid = False

        if is_valid:
            subscribes = set(subscribes)
            subscribers = models.Subscriber.objects.filter(email__iexact=email_form.cleaned_data['email'])
            if subscribers:
                subscriber = subscribers[0]
                exists_subscribes = list(subscriber.subscribe.all())
                for subscribe in subscribes:
                    if subscribe not in exists_subscribes:
                        subscriber.subscribe.add(subscribe)
                        models.log_subscribing(user, subscribe, action=models.SUBSCRIBING_LOG_ACTIONS['subscribe'])
                for exists_subscribe in exists_subscribes:
                    if exists_subscribe not in subscribes:
                        subscriber.subscribe.remove(exists_subscribe)
                        models.log_subscribing(user, exists_subscribe,
                                               action=models.SUBSCRIBING_LOG_ACTIONS['unsubscribe'])
            else:
                subscriber = models.Subscriber(user=user, email=email)
                subscriber.save()
                for subscribe in set(subscribes):
                    subscriber.subscribe.add(subscribe)
                    models.log_subscribing(user, subscribe, action=models.SUBSCRIBING_LOG_ACTIONS['subscribe'])
            return render(request, 'subscribe/frontend/subscribes_edited.html')
    else:
        email_form = EmailForm(initial={
            'email': email
        })
        forms = []
        for group in groups:
            initial_subscribes = []
            if email:
                subscribers = models.Subscriber.objects.filter(email__iexact=email)
                if subscribers:
                    subscriber = subscribers[0]
                    initial_subscribes = subscriber.subscribe.all()
            SubscriberForm = get_subscriber_form(
                models.Subscribe.objects.filter(group=group, is_active=True, hidden=False))
            forms.append({
                'group': group,
                'form': SubscriberForm(prefix=group.id, initial={
                    'subscribes': initial_subscribes
                })
            })
    return render(request, 'subscribe/frontend/index.html', {
        'forms': forms,
        'email_form': email_form
    })


def subscription_detail(request, id):
    subscribe = get_object_or_404(models.Subscribe, id=id, is_active=True)
    user_subscribed = False
    key = ''
    email = ''
    if request.user.is_authenticated:
        subscribers = models.Subscriber.objects.filter(email__iexact=email)
        if subscribers:
            subscriber = subscribers[0]
            user_subscribed = True
            key = models.generate_key(subscriber.id, subscriber.email)
            email = subscriber.email
    return render(request, 'subscribe/frontend/subscribe_detail.html', {
        'subscribe': subscribe,
        'user_subscribed': user_subscribed,
        'key': key,
        'email': email
    })


@transaction.atomic()
def subscribe(request, id):
    subscribe = get_object_or_404(models.Subscribe, id=id, is_active=True)
    email = ''

    if request.user.is_authenticated:
        user = request.user
        email = user.email

    if request.method == 'POST':
        form = models.SubscribeForm(request.POST)
        if form.is_valid():
            subscriber = models.Subscriber(email__iexact=form.cleaned_data['email'], subscribe=subscribe)
            subscriber.save()
            return render(request, 'subscribe/frontend/to_subscribe_success.html', {
                'subscribe': subscribe,
                'email': subscriber.email
            })

    else:
        form = models.SubscribeForm(initial={
            'email': email,
            'subscribe': subscribe.id
        })
    return render(request, 'subscribe/frontend/to_subscribe.html', {
        'subscribe': subscribe,
        'form': form,
    })


RUS_ABC = 'абвгдежзиклмнопрстуфхцчшщэюя'


@transaction.atomic()
@login_required
def journals(request):
    group = get_object_or_404(models.Group, name='Журналы')

    # all_subscribes = models.Subscribe.objects.values('id', 'name').filter(group=group)
    # a_to_z = set()
    #
    # for subscribe in all_subscribes:
    #     clear_name = subscribe['name'].lower().strip()
    #     if clear_name.startswith('the '):
    #         clear_name = clear_name[4:]
    #
    #     if clear_name.startswith('a '):
    #         clear_name = clear_name[2:]
    #
    #     a_to_z.add(clear_name[0])
    #
    # a_to_z_groups = {
    #     'rus': [],
    #     'other': [],
    # }
    #
    # for letter in sorted(a_to_z):
    #     if letter in RUS_ABC:
    #         a_to_z_groups['rus'].append(letter)
    #     else:
    #         a_to_z_groups['other'].append(letter)

    q = Q(group=group)

    # filtered = False
    #
    # letter = request.GET.get('letter', '')
    #
    # if letter:
    #     letter = letter.upper().strip()
    #     q &= Q(name__istartswith=letter)
    #     filtered = True
    #
    # filter_name = request.GET.get('name', '')
    #
    # if filter_name:
    #     qname = Q()
    #     filter_name_parts = filter_name.split()
    #     for filter_name_part in filter_name_parts:
    #         qname &= Q(name__icontains=filter_name_part.strip())
    #     q &= qname
    #     filtered = True
    # subscribes_page = get_page(request, models.Subscribe.objects.filter(q).order_by('name'))
    # subscribe_ids = set()
    #
    # for subscribe in subscribes_page.object_list:
    #     subscribe_ids.add(subscribe.id)

    try:
        subscriber = models.Subscriber.objects.get(user=request.user)
    except models.Subscriber.DoesNotExist:
        subscriber = models.Subscriber(user=request.user)
        subscriber.save()

    current_subscribe_ids = set()

    for subscribe in subscriber.subscribe.values('id').filter(group_id=group.id).order_by('name'):
        current_subscribe_ids.add(subscribe['id'])


    current_subscribes = []
    for subscribe in subscriber.subscribe.values('id', 'name').filter(group=group).order_by('name'):
        current_subscribes.append(subscribe)
    return render(request, 'subscribe/frontend/journals.html', {
        'group': group,
        # 'subscribes_page': subscribes_page,
        'current_subscribe_ids': current_subscribe_ids,
        'current_subscribes': current_subscribes,
        # 'a_to_z_groups': a_to_z_groups,
        # 'filtered': filtered,
    })


@transaction.atomic()
@login_required
def subscribe_ajax(request, id):
    subscribe = get_object_or_404(models.Subscribe, id=id)

    try:
        subscriber = models.Subscriber.objects.get(user=request.user)
    except models.Subscriber.DoesNotExist:
        subscriber = models.Subscriber(user=request.user)
        subscriber.save()

    if not subscriber.subscribe.filter(id=subscribe.id).exists():
        subscriber.subscribe.add(subscribe)

    return HttpResponse(json.dumps({'result': 'success'}))


@transaction.atomic()
@login_required
def unsubscribe_ajax(request, id):
    try:
        subscribe = models.Subscribe.objects.get(id=id)
    except models.Subscribe.DoesNotExist:
        return HttpResponse(json.dumps({'result': 'success'}))

    try:
        subscriber = models.Subscriber.objects.get(subscribe=subscribe, user=request.user)
        subscriber.subscribe.remove(subscribe)
    except models.Subscriber.DoesNotExist:
        return HttpResponse(json.dumps({'result': 'error', 'message': 'not found'}), status=404)

    return HttpResponse(json.dumps({'result': 'success'}))


# @transaction.atomic()
# @login_required
# def is_have_subscribe(request):
#     code = request.GET.get('code')
#     if not code:
#         return HttpResponse('Неправильные параметры запроса', status=400)
#
#     try:
#         subscribe = models.Subscribe.objects.get(code=code)
#     except models.Subscribe.DoesNotExist:
#         return HttpResponse(json.dumps({'result': 'success', 'status': False}))




@transaction.atomic()
def unsubscribe(request, id):
    subscribe = get_object_or_404(models.Subscribe, id=id)
    confirm = request.GET.get('confirm', None)
    email = request.GET.get('email', None)
    key = request.GET.get('key', None)
    if not email and request.user.is_authenticated:
        email = request.user.email

    if not email:
        return HttpResponse('Неправильные параметры запроса')

    subscriber = get_object_or_404(models.Subscriber, subscribe=subscribe, email__iexact=email)

    if key != models.generate_key(subscriber.id, email):
        return HttpResponse('Неправильная подпись заявки')
    if confirm:
        subscriber.delete()
        return render(request, 'subscribe/frontend/unsubscribe_success.html', {
            'subscribe': subscribe,
            'email': email
        })
    return render(request, 'subscribe/frontend/unsubscribe.html', {
        'subscribe': subscribe,
        'email': email
    })


@transaction.atomic()
def send_letters_req(request):
    models.send_letters()
    return HttpResponse('Ok')


@transaction.atomic()
def send_emails_req(request):
    models.send_to_email()
    return HttpResponse('Ok')