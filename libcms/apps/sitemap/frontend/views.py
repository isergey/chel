# coding=utf-8
from django.shortcuts import render


def index(request):
    return render(request, 'sitemap/frontend/index.html', content_type='application/xml')


def custom(request):
    return render(request, 'sitemap/frontend/custom.html', content_type='application/xml')
