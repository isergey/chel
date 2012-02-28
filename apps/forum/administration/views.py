# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse


def index(request):
    return render(request, 'pages/administration/index.html')


