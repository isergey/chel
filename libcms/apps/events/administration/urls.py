# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^events/$', views.events_list, name="events_list"),
    re_path(r'^events/create/$', views.create_event, name="create_event"),
    re_path(r'^events/edit/(?P<id>\d+)/$', views.edit_event, name="edit_event"),
    re_path(r'^events/delete/(?P<id>\d+)/$', views.delete_event, name="delete_event"),
    re_path(r'^events/(?P<id>\d+)/participants/$', views.participants, name="participants"),
    re_path(r'^events/subscription/$', views.subscriptions, name="subscriptions"),
)
