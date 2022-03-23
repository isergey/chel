# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.utils import translation

from participants.models import Library
from ..models import Page, Content


def index(request, library_id):
    library = get_object_or_404(Library, id=library_id)
    cur_language = translation.get_language()
    page = get_object_or_404(Page, slug='index', deleted=False)
    try:
        content = Content.objects.get(page=page, lang=cur_language[:2])
    except Content.DoesNotExist:
        content = None

    return render(request, 'participants_pages/frontend/show.html', {
        'page': page,
        'content': content,
        'library':library
    })

def show(request, code, slug):
    library = get_object_or_404(Library, code=code)
    cur_language = translation.get_language()
    page = get_object_or_404(Page, url_path=slug, library=library, deleted=False)
    try:
        content = Content.objects.get(page=page, lang=cur_language[:2])
    except Content.DoesNotExist:
        content = None

    return render(request, 'participants_pages/frontend/show.html', {
        'page': page,
        'content': content,
        'library':library
    })
