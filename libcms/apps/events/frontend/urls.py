# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views
urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^(?P<id>\d+)/$', views.show , name="show"),
    re_path(r'^date/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', views.filer_by_date, name="events_by_date"),
    re_path(r'^favorits/$', views.favorit_events , name="favorit_events"),
    re_path(r'^favorits/(?P<id>\d+)/$', views.favorite_show , name="favorite_show"),
    re_path(r'^(?P<id>\d+)/add_to_favorite/$', views.add_to_favorits , name="add_to_favorits"),
    re_path(r'^(?P<id>\d+)/delete_from_favorite/$', views.delete_from_favorite , name="delete_from_favorite"),
    re_path(r'^(?P<id>\d+)/participant/$', views.participant , name="participant"),
    re_path(r'^(?P<id>\d+)/participant/delete/$', views.delete_participant, name="delete_participant"),
)
