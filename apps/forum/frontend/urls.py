# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import views
urlpatterns = patterns(views,
    url(r'^$', views.index , name="forums"),
    url(r'^(?P<slug>[_-w]+)/$', views.topics , name="topics"),
    url(r'^(?P<slug>[_-w]+)/(?P<id>\d+)/$', views.articles , name="articles"),
    url(r'^(?P<slug>[_-w]+)/(?P<id>\d+)/replay/(?P<aid>\d+)/$', views.articles , name="replay_article"),
    url(r'^(?P<slug>[_-w]+)/(?P<id>\d+)/edit/(?P<eid>\d+)/$', views.articles , name="edit_article"),
#    url(r'^(?P<slug>[_-a-z0-9]+)/(?P<id>\d+)/$', views.show , name="show_topic"),
)
