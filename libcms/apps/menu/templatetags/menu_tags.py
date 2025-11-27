from django import template
from django.utils.translation import get_language

from menu.models import Menu, MenuItemTitle


register = template.Library()


def __get_menu(menu_slug, path):
    lang = get_language()[:2]
    menu = Menu.objects.filter(slug=menu_slug).first()
    if menu is None:
        return ({
            'menu': None
        })

    nodes = list(menu.root_item.get_descendants().exclude(show=False))

    item_titles = list(MenuItemTitle.objects.filter(item__in=nodes, lang=lang))

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


@register.inclusion_tag('menu/tags/drow_menu.html', takes_context=True)
def drow_menu(context, menu_slug):
    path = context['request'].META['PATH_INFO']
    return __get_menu(menu_slug, path)


@register.inclusion_tag('menu/tags/drow_menu_default.html', takes_context=True)
def drow_menu_default(context, menu_slug):
    path = context['request'].META['PATH_INFO']
    return __get_menu(menu_slug, path)
