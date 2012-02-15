# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import forms as auth_forms

def index(request):
    return render(request, 'frontend/index.html')


#def login(request):
#    if request
#    return render(request, 'frontend/login.html')

def logout(request):
    pass

def register(request):
    pass