from django import template
from .. import models

register = template.Library()


@register.simple_tag
def is_internal_ip(ip):
    return models.is_internal_ip(ip)


@register.simple_tag
def is_ip_have_internet(ip):
    return models.is_ip_have_internet(ip)
