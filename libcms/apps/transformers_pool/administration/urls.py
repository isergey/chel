# -*- coding: utf-8 -*-
from django.conf.urls import *
import views

urlpatterns = patterns(views,
    url(r'^$', views.index, name="index"),
    url(r'^xslt/$', views.xslt, name="xslt"),
)
