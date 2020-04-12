# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^feedbacks/list/$', views.feedbacks_list , name="feedbacks_list"),
    re_path(r'^feedbacks/edit/(?P<id>\d+)/$', views.edit_feedback , name="edit_feedback"),
    re_path(r'^feedbacks/delete/(?P<id>\d+)/$', views.delete_feedback , name="delete_feedback"),
#    re_path(r'^news/$', views.news_list, name="news_list"),
#    re_path(r'^news/create/$', views.create_news , name="create_news"),
#    re_path(r'^news/edit/(?P<id>\d+)/$', views.edit_news, name="edit_news"),
#    re_path(r'^news/delete/(?P<id>\d+)/$', views.delete_news, name="delete_news"),
)