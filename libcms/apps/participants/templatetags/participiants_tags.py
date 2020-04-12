# -*- coding: utf-8 -*-
import json as simplejson
from django import template
from ..models import Library
register = template.Library()


def make_library_dict(library):
    return {
        'id': library.id,
        'code': library.code,
        'name': library.name,
        'postal_address': getattr(library, 'postal_address', "не указан"),
        'phone': getattr(library, 'phone', "не указан"),
        'plans': getattr(library, 'plans', "не указано"),
        'http_service': getattr(library, 'http_service', "не указан"),
        'latitude': library.latitude,
        'longitude': library.longitude,
        }

@register.inclusion_tag('participants/tags/cbs_list.html')
def cbs_map():
    cbs_list = Library.objects.filter(parent=None).order_by('weight')
    js_orgs = []
    for org in cbs_list:
        js_orgs.append(make_library_dict(org))

    js_orgs = simplejson.dumps(js_orgs, ensure_ascii=False)
    return {
        'cbs_list': cbs_list,
        'js_orgs': js_orgs
    }