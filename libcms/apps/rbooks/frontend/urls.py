# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from django.views.generic import TemplateView

from . import views

urlpatterns = (
    re_path(r'^$', views.show , name="show"),
    re_path(r'^(?P<book>[/_\-0-9A-Za-z]+)/book/$', views.book , name="book"),
    re_path(r'^(?P<book>[/_\-0-9A-Za-z]+)/draw/$', views.draw , name="draw"),
    re_path(r'^rbooks2/$', views.rbooks2, name="rbooks2"),
    re_path(r'^auth/$', TemplateView.as_view(template_name='rbooks/frontend/auth_required.html'), name="auth_required"),
)
