# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views
urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^send/$', views.send_feedback , name="send_feedback"),
)
