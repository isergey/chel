# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.show , name="show"),
    re_path(r'^(?P<book>[/_\-0-9A-Za-z]+)/book/$', views.book , name="book"),
    re_path(r'^(?P<book>[/_\-0-9A-Za-z]+)/draw/$', views.draw , name="draw"),
    re_path(r'^rbooks2/$', views.rbooks2, name="rbooks2"),
)
