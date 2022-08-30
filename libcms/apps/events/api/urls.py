# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^events$', views.events, name="events"),
    re_path(r'^categories$', views.categories, name="categories"),
    re_path(r'^age_categories$', views.age_categories, name="age_categories"),
    re_path(r'^addresses$', views.addresses, name="addresses"),
)
