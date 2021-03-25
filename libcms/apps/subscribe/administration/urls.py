# -*- coding: utf-8 -*-
from django.conf.urls import *

from . import views

urlpatterns = (
    url(r'^$', views.index, name="index"),
    url(r'^groups/$', views.groups, name="groups"),
    url(r'^groups/create/$', views.create_group, name="create_group"),
    url(r'^groups/(?P<id>\d+)/change/$', views.change_group, name="change_group"),
    url(r'^groups/(?P<id>\d+)/delete/$', views.delete_group, name="delete_group"),

    url(r'^subscribes/$', views.subscribes, name="subscribes"),
    url(r'^subscribes/(?P<group_id>\d+)/$', views.subscribes, name="subscribes"),
    url(r'^subscribes/create/$', views.create_subscribe, name="create_subscribe"),
    url(r'^subscribes/(?P<id>\d+)/change/$', views.change_subscribe, name="change_subscribe"),
    url(r'^subscribes/(?P<id>\d+)/delete/$', views.delete_subscribe, name="delete_subscribe"),

    url(r'^letters/$', views.letters, name="letters"),
    url(r'^letters/create/$', views.create_letter, name="create_letter"),
    url(r'^letters/(?P<id>\d+)/change/$', views.change_letter, name="change_letter"),
    url(r'^letters/(?P<id>\d+)/delete/$', views.delete_letter, name="delete_letter"),
    url(r'^letters/send/$', views.send_letters, name="send_letters"),

    url(r'^subscribers/$', views.subscribers, name="subscribers"),
    url(r'^subscribers/create/$', views.create_subscriber, name="create_subscriber"),
    url(r'^subscribers/(?P<id>\d+)/change/$', views.change_subscriber, name="change_subscriber"),
    url(r'^subscribers/(?P<id>\d+)/delete/$', views.delete_subscriber, name="delete_subscriber"),

    url(r'^send_statuses/$', views.send_statuses, name="send_statuses"),
    url(r'^send_statuses/(?P<id>\d+)/delete/$', views.delete_send_status, name="delete_send_status"),
    url(r'^send_statuses/delete/$', views.delete_all_send_statuses, name="delete_all_send_statuses"),

    url(r'^statistics/$', views.statistics, name="statistics"),
    url(r'^commands/$', views.commands, name="commands"),
    url(r'^commands/(?P<index>\d+)/run/$', views.run_command, name="run_command"),
)
