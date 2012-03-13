# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag('participants/participants_districts_list_tag.html')
def districts_list():
    from apps.participants.districts import districts_list as districts
    return {'districts': districts}
