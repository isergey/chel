# -*- ecoding: utf-8 -*-
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, urls):
    if type(urls) == str:
        if context['request'].path == urls:
            return "active"
        else:
            return ""

    if context['request'].path in (reverse(url) for url in urls.split()):
        return "active"
    return ""


@register.simple_tag(takes_context=True)
def active_path(context, urls):
    """
    Если адрес ссылки начинается с адреса запроса
    """
    if type(urls) == str:
        if context['request'].path.startswith(urls):
            return "active"
        else:
            return ""

    for url in urls.split():
        if context['request'].path.startswith(reverse(url)):
            return "active"
    return ""
