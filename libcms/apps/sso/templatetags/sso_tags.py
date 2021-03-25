import datetime
from django import template
from ..utils import get_logout_url

register = template.Library()


@register.simple_tag(takes_context=True)
def sso_logout_url(context):
    return get_logout_url(context.request)
