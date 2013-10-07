# -*- coding: utf-8 -*-
from django.conf.urls import *
import views
urlpatterns = patterns('',
    url(r'^$', views.show , name="show"),
    url(r'^(?P<book>[/_\-0-9A-Za-z]+)/book/$', views.book , name="book"),
    url(r'^(?P<book>[/_\-0-9A-Za-z]+)/draw/$', views.draw , name="draw"),


)
