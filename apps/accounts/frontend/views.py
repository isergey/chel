# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.contrib.auth import forms as auth_forms

from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.messages.api import get_messages

from social_auth import __version__ as version


def index(request):
    return render(request, 'frontend/index.html')


#def login(request):
#    if request
#    return render(request, 'frontend/login.html')

def logout(request):
    pass

def register(request):
    pass

def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated():
        return redirect('accounts:frontend:done')
    else:
        return render(request, 'frontend/oauth/home.html', {
            'version': version
        })

@login_required
def done(request):
    """Login complete view, displays user data"""
    ctx = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend')
    }
    return render(request, 'frontend/oauth/done.html', ctx)


def error(request):
    """Error view"""
    messages = get_messages(request)
    return render(request, 'frontend/oauth/error.html', {
        'version': version,
        'messages': messages
    })