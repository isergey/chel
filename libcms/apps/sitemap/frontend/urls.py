# -*- coding: utf-8 -*-
from django.conf.urls import *
import views

urlpatterns = (
    url(r'^sitemap.xml$', views.index, name="index"),
    url(r'^custom_sitemap.xml$', views.custom, name="custom"),
)
