# -*- coding: utf-8 -*-
from django.shortcuts import render


def index(request):
    return render(request, 'administration/index.html')



def users(request):
    return render(request, 'administration/index.html')