# -*- coding: utf-8 -*-
import os

from django.contrib import messages
from django.db.models import Q

try:
    import Image
except ImportError:
    from PIL import Image
import uuid
from datetime import datetime, timedelta
from common.pagination import get_page
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, resolve_url
from django.utils.translation import get_language
from guardian.decorators import permission_required_or_403

from .forms import NewsForm, NewsContentForm, SubscriptionFilterForm
from ..models import News, NewsContent
from .. import subscription

@login_required
@permission_required_or_403('news.add_news')
def index(request):
    return redirect('news:administration:news_list')


@login_required
@permission_required_or_403('news.add_news')
def news_list(request):
    type = request.GET.get('type', 'public')
    if type ==  'prof':
        news_page = get_page(request, News.objects.filter(type=1).order_by('-create_date'))
    elif type == 'public':
        news_page = get_page(request, News.objects.filter(type=0).order_by('-create_date'))
    else:
        news_page = get_page(request, News.objects.filter(type=2).order_by('-create_date'))

    _join_content(news_page.object_list)

    return render(request, 'news/administration/news_list.html', {
        'news_list': news_page.object_list,
        'news_page': news_page,
        })



@login_required
@permission_required_or_403('news.add_news')
@transaction.atomic
def create_news(request):

    if request.method == 'POST':
        news_form = NewsForm(request.POST,prefix='news_form')

        news_content_forms = []
        for lang in settings.LANGUAGES:
            news_content_forms.append({
                'form':NewsContentForm(request.POST,prefix='news_content' + lang[0]),
                'lang':lang[0]
            })

        if news_form.is_valid():



            valid = False
            for news_content_form in news_content_forms:
                valid = news_content_form['form'].is_valid()
                if not valid:
                    break

            if valid:
                news = news_form.save(commit=False)
                if 'news_form_avatar' in request.FILES:
                    try:
                        avatar_img_name = handle_uploaded_file(request.FILES['news_form_avatar'])
                    except IOError as e:
                        return HttpResponse('Возникла ошибка при загрузке аватарки:' + e.message)
                    news.avatar_img_name = avatar_img_name
                news.save()
                for news_content_form in news_content_forms:
                    news_content = news_content_form['form'].save(commit=False)
                    news_content.lang = news_content_form['lang']
                    news_content.news = news
                    news_content.save()
                return redirect('news:administration:news_list')
    else:
        news_form = NewsForm(prefix="news_form")
        news_content_forms = []
        for lang in settings.LANGUAGES:
            news_content_forms.append({
                'form':NewsContentForm(prefix='news_content' + lang[0]),
                'lang':lang[0]
            })

    return render(request, 'news/administration/create_news.html', {
        'news_form': news_form,
        'news_content_forms': news_content_forms,
        })

@login_required
@permission_required_or_403('news.change_news')
@transaction.atomic
def edit_news(request, id):
    news = get_object_or_404(News, id=id)
    news_contents = NewsContent.objects.filter(news=news)
    news_contents_langs = {}

    for lang in settings.LANGUAGES:
        news_contents_langs[lang] = None

    for news_content in news_contents:
        news_contents_langs[news_content.lang] = news_content

    if request.method == 'POST':
        news_form = NewsForm(request.POST,prefix='news_form', instance=news)

        if news_form.is_valid():
            news = news_form.save(commit=False)
            if 'news_form_avatar' in request.FILES:
                if news.avatar_img_name:
                    handle_uploaded_file(request.FILES['news_form_avatar'], news.avatar_img_name)
                else:
                    avatar_img_name = handle_uploaded_file(request.FILES['news_form_avatar'])
                    news.avatar_img_name = avatar_img_name
            news.save()
            news_content_forms = []
            for lang in settings.LANGUAGES:
                lang = lang[0]
                if lang in news_contents_langs:
                    news_content_forms.append({
                        'form':NewsContentForm(request.POST,prefix='news_content_' + lang, instance=news_contents_langs[lang]),
                        'lang':lang
                    })
                else:
                    news_content_forms.append({
                        'form':NewsContentForm(request.POST, prefix='news_content_' + lang),
                        'lang':lang
                    })


            valid = False
            for news_content_form in news_content_forms:
                valid = news_content_form['form'].is_valid()
                if not valid:
                    break

            if valid:
                for news_content_form in news_content_forms:
                    news_content = news_content_form['form'].save(commit=False)
                    news_content.news = news
                    news_content.lang = news_content_form['lang']
                    news_content.save()
                return redirect('news:administration:news_list')
    else:
        news_form = NewsForm(prefix="news_form", instance=news)
        news_content_forms = []
        for lang in settings.LANGUAGES:
            lang = lang[0]
            if lang in news_contents_langs:
                news_content_forms.append({
                    'form':NewsContentForm(prefix='news_content_' + lang, instance=news_contents_langs[lang]),
                    'lang':lang
                })
            else:
                news_content_forms.append({
                    'form':NewsContentForm(prefix='news_content_' + lang),
                    'lang':lang
                })

    return render(request, 'news/administration/edit_news.html', {
        'news_form': news_form,
        'news_content_forms': news_content_forms,
        })


@login_required
@permission_required_or_403('news.delete_news')
@transaction.atomic
def delete_news(request, id):
    news = get_object_or_404(News, id=id)
    news.delete()
    delete_avatar(news.avatar_img_name)
    return redirect('news:administration:news_list')


@login_required
@permission_required_or_403('news.create_news')
@transaction.atomic
def subscriptions(request):
    now = datetime.now()
    past = now - timedelta(days=7)

    start_date = past.date()
    end_date = now.date()

    if request.GET.get('filter'):
        filter_form = SubscriptionFilterForm(request.GET)
        if filter_form.is_valid():
            start_date = filter_form.cleaned_data['start_date']
            end_date = filter_form.cleaned_data['end_date']

    else:
        filter_form = SubscriptionFilterForm(initial={
            'start_date': start_date,
            'end_date': end_date
        })


    q = Q(create_date__gte=datetime(
        year=start_date.year,
        month=start_date.month,
        day=start_date.day,
        hour=0,
        minute=0,
        second=0
    ))

    q &= Q(create_date__lte=datetime(
        year=end_date.year,
        month=end_date.month,
        day=end_date.day,
        hour=23,
        minute=59,
        second=59
    ))

    news_list = News.objects.filter(q).order_by('-create_date')
    _join_content(news_list)

    if request.GET.get('subscription') == 'create_letter':
        letter = subscription.create_subscription_letter(news_list)
        if letter is not None:
            messages.success(request, 'Письмо создано - <a href="{url}">Перейти к письму</a>'.format(
                url=resolve_url('subscribe:administration:change_letter', id=letter.id)
            ))
        else:
            messages.warning(request, 'Письмо рассылки не было создано')

    return render(request, 'news/administration/subscriptions.html', {
        'news_list': news_list,
        'filter_form': filter_form,
    })

#def handle_uploaded_file(f, old_name=None):
#    upload_dir = settings.MEDIA_ROOT + 'uploads/newsavatars/'
#    now = datetime.now()
#    dirs = [
#        upload_dir,
#        upload_dir  + str(now.year) + '/',
#        upload_dir  + str(now.year) + '/' + str(now.month) + '/',
#        ]
#    for dir in dirs:
#        if not os.path.isdir(dir):
#            os.makedirs(dir, 0744)
#    size = 147, 110
#    if old_name:
#        name = old_name
#    else:
#        name = str(now.year) + '/' + str(now.month) + '/' + uuid.uuid4().hex + '.jpg'
#    path = upload_dir + name
#    with open(path, 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)
#    im = Image.open(path)
#    im = im.resize(size, Image.ANTIALIAS)
#    im.save(path, "JPEG",  quality=95)
#    return name


def handle_uploaded_file(f, old_name=None):
    upload_dir = settings.MEDIA_ROOT + 'uploads/newsavatars/'
    now = datetime.now()
    dirs = [
        upload_dir,
        upload_dir  + str(now.year) + '/',
        upload_dir  + str(now.year) + '/' + str(now.month) + '/',
        ]
    for dir in dirs:
        if not os.path.isdir(dir):
            os.makedirs(dir, 0o744)
    size = 147, 110
    if old_name:
        name = old_name
    else:
        name = str(now.year) + '/' + str(now.month) + '/' + uuid.uuid4().hex + '.jpg'
    path = upload_dir + name
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    im = Image.open(path)
    image_width = im.size[0]
    image_hight = im.size[1]
    image_ratio = float(image_width) / image_hight

    box = [0, 0, 0, 0]
    if image_ratio <= 1:
        new_hight = int(image_width / 1.333)
        vert_offset = int((image_hight - new_hight) / 2)
        box[0] = 0
        box[1] = vert_offset
        box[2] = image_width
        box[3] = vert_offset + new_hight
    else:
        new_width = image_hight * 1.333
        if new_width > image_width:
            new_width = image_width
            new_hight = int(new_width / 1.333)
            vert_offset = int((image_hight - new_hight) / 2)
            box[0] = 0
            box[1] = vert_offset
            box[2] = new_width
            box[3] = vert_offset + new_hight
        else:
            gor_offset = int((image_width - new_width) / 2)
            box[0] = gor_offset
            box[1] = 0
            box[2] = int(gor_offset + new_width)
            box[3] = image_hight

    im = im.crop(tuple(box))

    final_hight = 660
    image_ratio = float(im.size[0]) / im.size[1]
    final_width = int((image_ratio * final_hight))
    im = im.resize((final_width, final_hight), Image.ANTIALIAS)
    im = im.convert('RGB')
    im.save(path, "JPEG",  quality=95)
    return name


def delete_avatar(name):
    if not name:
        return
    upload_dir = settings.MEDIA_ROOT + 'uploads/newsavatars/'
    if os.path.isfile(upload_dir + name):
        os.remove(upload_dir + name)


def _join_content(news_list):
    news_contents = NewsContent.objects.filter(news__in=list(news_list), lang=get_language()[:2])
    t_dict = {}
    for news in news_list:
        t_dict[news.id] = {'news': news}

    for news_content in news_contents:
        t_dict[news_content.news_id]['news'].news_content = news_content