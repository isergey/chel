# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^(?P<poll_id>\d+)/$', views.vote , name="vote"),
    re_path(r'^(?P<poll_id>\d+)/results/$', views.results , name="results"),
#    re_path(r'^rss/$', feeds.LatestEntriesFeed(), name='rss'),
)
