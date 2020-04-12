# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^create$', views.create, name="create"),
    re_path(r'^edit/(?P<poll_id>\d+)/$', views.edit, name="edit"),
    re_path(r'^delete/(?P<poll_id>\d+)/$', views.delete, name="delete"),

    re_path(r'^view/(?P<poll_id>\d+)/$', views.view, name="view"),
    re_path(r'^create/choice/(?P<poll_id>\d+)/$', views.create_choice, name="create_choice"),
    re_path(r'^edit/choice/(?P<choice_id>\d+)/$', views.edit_choice, name="edit_choice"),
    re_path(r'^delete/choice/(?P<choice_id>\d+)/$', views.delete_choice, name="delete_choice"),

)