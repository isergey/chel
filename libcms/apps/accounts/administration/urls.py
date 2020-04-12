# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^users$', views.users_list, name="users_list"),
    re_path(r'^users/create/$', views.create_user, name="create_user"),
    re_path(r'^users/edit/(?P<id>\d+)/$', views.edit_user, name="edit_user"),
    re_path(r'^groups/$', views.groups_list, name='groups_list'),
    re_path(r'^groups/create/$', views.create_group, name="create_group"),
    re_path(r'^groups/edit/(?P<id>\d+)/$', views.edit_group, name="edit_group"),
    re_path(r'^groups/delete/(?P<id>\d+)/$', views.delete_group, name="delete_group"),
)
