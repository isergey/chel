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

    sc = _get_or_set_sc(request)

    create_record(
        request=request,
        sc=sc,
        action=action,
        attributes=attributes
    )

    return redirect(to_url)


def _get_or_set_sc(request):
    sc = request.COOKIES.get('_sc')
    if sc is None:
        sc = str(uuid4())
        request.set_cookie(
            key='_sc',
            value=sc,
            max_age=31536000
        )
    return sc
