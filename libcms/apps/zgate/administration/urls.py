# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="administration_zgate_index"),
    re_path(r'^create$', views.create, name="administration_zgate_create"),
    re_path(r'^edit/(?P<id>\d+)/$', views.edit, name="administration_zgate_edit"),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name="administration_zgate_delete"),
    re_path(r'^statistics/$', views.statistics, name="administration_zgate_statistics"),
)

