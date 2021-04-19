# -*- coding: utf-8 -*-
from django.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^redirect$', views.redirect_to_url , name="redirect_to_url"),
)
