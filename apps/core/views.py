# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.utils.translation import check_for_language
from django.utils.translation import ugettext as _
from django.shortcuts import HttpResponse, render
from django.utils import translation



def index(request):
    return HttpResponse( _('Hello'))


def select_language(request):
    """
    Отображает форму выбора языка
    """
    return render(request, 'i18n/select_lang_form.html')

def set_language(request):
    """
    Redirect to a given url while setting the chosen language in the
    session or cookie. The url and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    translation.activate(lang_code)
    return response