# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^ask$', views.ask , name="ask"),
    re_path(r'^detail/(?P<id>\d+)/', views.detail, name="detail"),
    re_path(r'^detail/print/(?P<id>\d+)/', views.printed_detail, name="printed_detail"),
    re_path(r'^my/', views.my_questions , name="my_questions"),
#    re_path(r'^detail/', views.detail , name="detail"),
#    re_path(r'^(?P<slug>[/_\-0-9A-Za-z]+)/$', views.show , name="show"),
)

