# -*- coding: utf-8 -*-
from django import template
from django.utils import translation

from ..models import Content

register = template.Library()


@register.filter
def get_cur_lang_content(page):
    cur_language = translation.get_language()
    try:
        content = Content.objects.get(page=page, lang=cur_language[:2])
    except Content.DoesNotExist:
        content = None
    return content


@register.inclusion_tag('pages/templatetags/render_page_content.html')
def render_page_content(slug):
    cur_language = translation.get_language()
    try:
        content = Content.objects.get(page__url_path=slug, page__deleted=False, lang=cur_language[:2]).content
    except Content.DoesNotExist:
        content = ''
    return {
        'content': content
    }
