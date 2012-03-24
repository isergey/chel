# -*- coding: utf-8 -*-
from django import template
from django.utils import translation
from django.utils.translation import to_locale, get_language
from menu.models import Menu, MenuItemTitle

register = template.Library()
@register.inclusion_tag('menu/tags/drow_menu.html', takes_context=True)
def drow_menu(context, menu_slug):
    path = context['request'].META['PATH_INFO']
    try:
        menu = Menu.objects.get(slug=menu_slug)
    except Menu.DoesNotExist:
        return ({
            'menu': None
        })

    nodes = list(menu.root_item.get_descendants())
    lang=get_language()[:2]
    item_titles = MenuItemTitle.objects.filter(item__in=nodes, lang=lang)
    nd = {}
    for node in nodes:
        nd[node.id] = node

    for item_title in item_titles:
        nd[item_title.item_id].item_title = item_title

    if not item_titles:
        nodes = []
    return ({
        'nodes': nodes,
        'menu': menu,
        'path': path
    })

