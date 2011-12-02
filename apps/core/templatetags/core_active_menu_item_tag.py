# encoding: utf-8 -*-
#from django import template
#register = template.Library()
#
#@register.inclusion_tag('pagination_tag.html', takes_context=True)
#def pagination(context, objects_list):
#    request = context['request']
#    return {'objects_list': objects_list,
#            'request':request
#    }
import re
from django import template

register = template.Library()

@register.simple_tag
def active(request, pattern):
    if re.search(pattern, request.path):
        return 'active'
    return ''