# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.utils import translation
from django.utils.translation import get_language
from django.db.models import Q
from common.pagination import get_page
from ..models import News, NewsContent


def index(request):
    news_type = request.GET.get('type', '')
    query = Q(publicated=True)

    if news_type == 'chel':
        query = query & Q(type=0)
    if news_type == 'lib':
        query = query & Q(type=1)

    news_page = get_page(request, News.objects.filter(query).order_by('-create_date'))

    news_contents = list(NewsContent.objects.filter(news__in=list(news_page.object_list), lang=get_language()[:2]))

    t_dict = {}
    for news in news_page.object_list:
        t_dict[news.id] = {
            'news': news
        }

    for news_content in news_contents:
        t_dict[news_content.news_id]['news'].news_content = news_content

    return render(request, 'news/frontend/list.html', {
        'news_list': news_page.object_list,
        'news_page': news_page,
    })


def show(request, id):
    cur_language = translation.get_language()
    try:
        news = News.objects.get(id=id)
    except News.DoesNotExist:
        raise Http404()

    try:
        content = NewsContent.objects.get(news=news, lang=cur_language[:2])
    except Content.DoesNotExist:
        content = None

    return render(request, 'news/frontend/show.html', {
        'news': news,
        'content': content
    })


def sitemap(request):
    news = News.objects.values('id').filter(publicated=True).order_by('-create_date')
    return render(
        request, 'news/frontend/sitemap.html', {
            'news': news
        },
        content_type='application/xml'
    )
