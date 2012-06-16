# coding: utf-8
from django.shortcuts import render

def index(request):
    return render(request, 'index/frontend/index.html')

def slider(request):
    return render(request, 'slider.html')