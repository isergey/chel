# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.utils import translation
from django.contrib.auth.models import Group
from guardian.shortcuts import get_perms
from ..models import Page, Content, ViewLog

PAGES = getattr(settings, 'PAGES', {})
CHECK_SHOW_PERMISSION = PAGES.get('check_show_permission', False)

def index(request):
    cur_language = translation.get_language()
    page = get_object_or_404(Page, slug='index', public=True)
    try:
        content = Content.objects.get(page=page, lang=cur_language[:2])
    except Content.DoesNotExist:
        content = None

    return render(request, 'pages/frontend/show.html', {
        'page': page,
        'content': content
    })


def show(request, slug):

    cur_language = translation.get_language()
    page = get_object_or_404(Page, url_path=slug, public=True)
    if CHECK_SHOW_PERMISSION:
        if not request.user.is_authenticated():
            anaons = Group.objects.get(name='anonymouses')
            if 'view_page' not in get_perms(anaons, page):
                raise PermissionDenied()
        else:
            if not request.user.has_perm('view_page', page):
                raise PermissionDenied()

    try:
        content = Content.objects.get(page=page, lang=cur_language[:2])
    except Content.DoesNotExist:
        content = None
    children = None

    #    if not page.is_leaf_node():
    #        children = list(Page.objects.filter(parent=page, public=True))
    #        contents = Content.objects.filter(page__in=children, lang=cur_language[:2])
    #        cd = {}
    #        for child in children:
    #            cd[child.id] = child
    #
    #        for contend_page in contents:
    #            if contend_page.page_id in cd:
    #                cd[contend_page.page_id].content = contend_page

    user = request.user
    log = ViewLog(page=page)
    if not user.id:
        log.user_id = -1
    else:
        log.user = user
    log.save()
    return render(request, 'pages/frontend/show.html', {
        'page': page,
        'content': content,
    })
