# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^sitemap.xml$', views.index, name="index"),
    re_path(r'^sitemap_(?P<offset>\d+).xml$', views.records, name="records"),
)