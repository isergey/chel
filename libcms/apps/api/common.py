# encoding: utf-8
import json as simplejson
from django.http import HttpResponse



def response(data={}):
    if not isinstance(data, dict):
        raise TypeError('data must be dict type object')
    return HttpResponse(simplejson.dumps(data, ensure_ascii=False), content_type='application/json; charset=utf8')


