# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^auth_user/$', views.auth_user, name="auth_user"),
    re_path(r'^get_user_orgs/$', views.get_user_orgs, name="get_user_orgs"),
    re_path(r'^get_org/$', views.get_org, name="get_org"),
    re_path(r'^find_orgs/$', views.find_orgs, name="find_orgs"),
    re_path(r'^get_user/$', views.get_user, name="get_user"),
)
