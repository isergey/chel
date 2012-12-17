# encoding: utf-8

from django.conf.urls import *

import views

urlpatterns = patterns('',
   url(r'^$', views.index , name="index"),
   url(r'^detail/(?P<id>\d+)/', views.detail , name="detail"),
)