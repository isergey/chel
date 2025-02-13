# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^pages/$', views.pages_list, name="pages_list"),
    re_path(r'^pages/(?P<parent>\d+)/$', views.pages_list, name="pages_list"),
    re_path(r'^pages/create/$', views.create_page , name="create_page"),
    re_path(r'^pages/create/(?P<parent>\d+)/$', views.create_page , name="create_page"),
    re_path(r'^pages/edit/(?P<id>\d+)/$', views.edit_page, name="edit_page"),
    re_path(r'^pages/delete/(?P<id>\d+)/$', views.delete_page, name="delete_page"),
    re_path(r'^pages/content/create/(?P<page_id>\d+)/$', views.create_page_content, name="create_page_content"),
    re_path(r'^pages/content/edit/(?P<page_id>\d+)/(?P<lang>[a-z]{2})$', views.edit_page_content, name="edit_page_content"),


    re_path(r'^pages/up/(?P<id>\d+)/$', views.page_up , name="page_up"),
    re_path(r'^pages/down/(?P<id>\d+)/$', views.page_down , name="page_down"),
)