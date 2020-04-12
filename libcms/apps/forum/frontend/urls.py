# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.forums , name="forums"),

    re_path(r'^forum_permissions/(?P<id>\d+)/$', views.forum_permissions , name="forum_permissions"),
    re_path(r'^forum_permissions/(?P<id>\d+)/(?P<gid>\d+)/$', views.assign_forum_permissions , name="assign_forum_permissions"),

    re_path(r'^topic_permissions/(?P<id>\d+)/$', views.topic_permissions , name="topic_permissions"),
    re_path(r'^topic_permissions/(?P<id>\d+)/(?P<gid>\d+)/$', views.assign_topic_permissions , name="assign_topic_permissions"),

    re_path(r'^article_delete/(?P<id>\d+)/$', views.article_delete , name="article_delete"),
    re_path(r'^article_hide/(?P<id>\d+)/$', views.article_hide , name="article_hide"),
    re_path(r'^article_show/(?P<id>\d+)/$', views.article_show , name="article_show"),
    re_path(r'^topic_delete/(?P<id>\d+)/$', views.topic_delete , name="topic_delete"),
    re_path(r'^topic_open/(?P<id>\d+)/$', views.topic_open , name="topic_open"),
    re_path(r'^topic_close/(?P<id>\d+)/$', views.topic_close , name="topic_close"),
    re_path(r'^forum_delete/(?P<id>\d+)/$', views.forum_delete , name="forum_delete"),

    re_path(r'^article_preview/$', views.article_preview , name="article_preview"),

    re_path(r'^(?P<slug>[a-zA-Z0-9-_]+)/$', views.forum_topics , name="topics"),
    re_path(r'^(?P<slug>[a-zA-Z0-9-_]+)/(?P<id>\d+)/$', views.topic_articles , name="articles"),
    re_path(r'^(?P<slug>[a-zA-Z0-9-_]+)/(?P<id>\d+)/replay/(?P<aid>\d+)/$', views.topic_articles , name="replay_article"),
    re_path(r'^(?P<slug>[a-zA-Z0-9-_]+)/(?P<id>\d+)/edit/(?P<eid>\d+)/$', views.topic_articles , name="edit_article"),
    #    re_path(r'^(?P<slug>[_-a-z0-9]+)/(?P<id>\d+)/$', views.show , name="show_topic"),
)