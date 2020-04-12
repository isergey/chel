# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    # Индексная страница
    re_path(r'^$', views.index, name="index"),
    re_path(r'^select_language/$', views.select_language, name="select_language"),
    re_path(r'^set_language/', views.set_language, name='set_language'),


)
