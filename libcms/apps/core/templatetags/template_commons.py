__author__ = 'sergey'
from django.template import Library

register = Library()


@register.simple_tag()
def get_object_key(object, key):
    if not object:
        object = {}
    return object.get(key, key)
