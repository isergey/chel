# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required
from common.pagination import get_page
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.utils.translation import to_locale, get_language

from core.forms import LanguageForm
from ..models import News, NewsContent
from forms import NewsForm, NewsContentForm

@login_required
@permission_required_or_403('news.add_news')
def index(request):
    return redirect('news:administration:news_list')


@login_required
@permission_required_or_403('news.add_news')
def news_list(request):
    type = request.GET.get('type', u'public')
    if type ==  u'prof':
        news_page = get_page(request, News.objects.filter(type=1).order_by('-create_date'))
    elif type == u'public':
        news_page = get_page(request, News.objects.filter(type=0).order_by('-create_date'))
    else:
        news_page = get_page(request, News.objects.filter(type=2).order_by('-create_date'))

    news_contents = list(NewsContent.objects.filter(news__in=list(news_page.object_list), lang=get_language()[:2]))

    t_dict = {}
    for news in news_page.object_list:
        t_dict[news.id] = {'news': news}

    for news_content in news_contents:
        t_dict[news_content.news_id]['news'].news_content = news_content

    return render(request, 'news/administration/news_list.html', {
        'news_list': news_page.object_list,
        'news_page': news_page,
        })



@login_required
@permission_required_or_403('news.add_news')
@transaction.commit_on_success
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
                    avatar_img_name = handle_uploaded_file(request.FILES['news_form_avatar'])
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
@transaction.commit_on_success
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
@transaction.commit_on_success
def delete_news(request, id):
    news = get_object_or_404(News, id=id)
    news.delete()
    delete_avatar(news.avatar_img_name)
    return redirect('news:administration:news_list')




import os
import Image
import uuid
from datetime import datetime
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
            os.makedirs(dir, 0744)
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

    final_hight = 110
    image_ratio = float(im.size[0]) / im.size[1]
    final_width = int((image_ratio * final_hight))
    im = im.resize((final_width, final_hight), Image.ANTIALIAS)
    im.save(path, "JPEG",  quality=95)
    return name

def delete_avatar(name):
    upload_dir = settings.MEDIA_ROOT + 'uploads/newsavatars/'
    if os.path.isfile(upload_dir + name):
        os.remove(upload_dir + name)
