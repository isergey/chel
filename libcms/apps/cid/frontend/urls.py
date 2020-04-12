# encoding: utf-8

from django.conf.urls import re_path

from . import views

urlpatterns = (
   re_path(r'^$', views.index , name="index"),
   re_path(r'^detail/(?P<id>\d+)/$', views.detail , name="detail"),
   re_path(r'^indexing/$', views.index_sid , name="index_sid"),
)