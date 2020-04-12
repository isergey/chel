# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views
#import feeds
urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^(?P<id>\d+)/$', views.show , name="show"),
#    re_path(r'^rss/$', feeds.LatestEntriesFeed(), name='rss'),
)
