# -*- coding: utf-8 -*-
from django.conf.urls import *
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name="index"),
    url(r'^users$', views.users_list, name="users_list"),
    url(r'^users/create/$', views.create_user, name="create_user"),
    url(r'^users/edit/(?P<id>\d+)/$', views.edit_user, name="edit_user"),
    url(r'^groups/$', 'groups_list', name=views.groups_list),
    url(r'^groups/create/$', views.create_group, name="create_group"),
    url(r'^groups/edit/(?P<id>\d+)/$', views.edit_group, name="edit_group"),
    url(r'^groups/delete/(?P<id>\d+)/$', views.delete_group, name="delete_group"),
)
