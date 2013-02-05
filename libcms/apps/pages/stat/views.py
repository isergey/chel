# -*- coding: utf-8 -*-
from django.shortcuts import HttpResponse
from guardian.shortcuts import get_perms


def index(request):
    return HttpResponse(u'ok')
