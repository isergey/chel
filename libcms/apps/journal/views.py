from urllib.parse import unquote
from uuid import uuid4
import base64
from django.shortcuts import HttpResponse, redirect
from django.views.decorators.cache import never_cache

from .models import create_record


@never_cache
def index(request):
    action = request.GET['a']
    sc, is_new = _get_sc(request)
    attributes = {}

    for attr, value in request.GET.items():
        if len(attr) > 5 and ''.startswith('attr_'):
            attributes[attr[5:]] = value[0:512]

    create_record(
        request=request,
        sc=sc,
        action=action,
        attributes=attributes
    )

    response = HttpResponse('')
    _set_sc_cookie(response, is_new, sc)
    return response


@never_cache
def redirect_to_url(request):
    to_url:str = request.GET['u']
    action = request.GET['a'][0:256]

    if not to_url.startswith('http'):
        to_url = __decode_base64_url(to_url)

    attributes = {
        'to_url': to_url[0:1024],
    }

    for attr, value in request.GET.items():
        if len(attr) > 5 and attr.startswith('attr_'):
            attributes[attr[5:]] = value[0:128]

    sc, is_new = _get_sc(request)

    create_record(
        request=request,
        sc=sc,
        action=action,
        attributes=attributes
    )

    response = redirect(to_url)
    _set_sc_cookie(response, is_new, sc)
    return response


def _get_sc(request):
    sc = request.COOKIES.get('_sc')
    is_new = False
    if sc is None:
        sc = str(uuid4())
        is_new = True
    return sc, is_new


def _set_sc_cookie(response, is_new, sc):
    if is_new:
        response.set_cookie(
            key='_sc',
            value=sc,
            max_age=31536000
        )


def __decode_base64_url(b64_string: str):
    s = base64.urlsafe_b64decode(b64_string)
    return unquote(s)
