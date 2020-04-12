# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views
from . import feeds
urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^(?P<id>\d+)/$', views.show , name="show"),
    re_path(r'sitemap.xml$', views.sitemap, name="sitemap"),
    re_path(r'^rss/$', feeds.LatestEntriesFeed(), name='rss'),
)
