from uuid import uuid4
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.cache import never_cache

from .models import create_record


@never_cache
def index(request):
    action = request.GET['a']
    sc = _get_or_set_sc(request)
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

    return HttpResponse('')


@never_cache
def redirect_to_url(request):
    to_url = request.GET['u']
    action = request.GET['a'][0:256]

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
    if is_new:
        request.set_cookie(
            key='_sc',
            value=sc,
            max_age=31536000
        )
    return response


def _get_sc(request):
    sc = request.COOKIES.get('_sc')
    is_new = False
    if sc is None:
        sc = str(uuid4())
        is_new = True
    return sc, is_new
