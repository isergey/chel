# -*- encoding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^show/(?P<id>\d+)/$', views.album_view, name="album_view")
)
