# -*- coding: utf-8 -*-
from django.conf.urls import *
from . import views

urlpatterns = (
    url(r'^$', views.index, name="index"),
    url(r'^upload_file/$', views.upload_file, name="upload_file"),
    url(r'^delete/(?P<file_id>\d+)/$', views.delete, name="delete"),
    url(r'^ajax_file_info/$', views.ajax_file_info,  name="ajax_file_info"),
)