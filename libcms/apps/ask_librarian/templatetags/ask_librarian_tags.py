# -*- coding: utf-8 -*-
from django import template
from django.utils.translation import get_language
from ..models import Category, CategoryTitle

register = template.Library()
@register.inclusion_tag('ask_librarian/tags/drow_categories_tree.html', takes_context=True)
def drow_categories_tree(context):
    path = context['request'].META['PATH_INFO']

    nodes = list(Category.objects.all())
    lang=get_language()[:2]
    nodes_titles = CategoryTitle.objects.filter(category__in=nodes, lang=lang)
    nd = {}
    for node in nodes:
        nd[node.id] = node

    for node_title in nodes_titles:
        nd[node_title.category_id].node_title = node_title

    if not nodes_titles:
        nodes = []
    return ({
        'nodes': nodes,
        'path': path
    })

