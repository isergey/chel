# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, urls):
    """
    Если адрес ссылки совпадает с адресом запроса
    """
    if context['request'].path in ( reverse(url) for url in urls.split() ):
        return "active"
    return ""


@register.simple_tag(takes_context=True)
def active_path(context, urls):
    """
    Если адрес ссылки начинается с адреса запроса
    """
    for url in urls.split():
        if context['request'].path.startswith(reverse(url)):
            return "active"
    return ""