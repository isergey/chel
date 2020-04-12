# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^sitemap.xml$', views.sitemap, name="sitemap"),
    re_path(r'^(?P<slug>[/_\-0-9A-Za-z]+)/$', views.show , name="show"),
)
