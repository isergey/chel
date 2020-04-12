# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^list/$', views.list, name="list"),
    re_path(r'^list/(?P<parent>\d+)/$', views.list, name="list"),
    re_path(r'^create/$', views.create , name="create"),
    re_path(r'^create/(?P<parent>\d+)/$', views.create , name="create"),
    re_path(r'^edit/(?P<id>\d+)/$', views.edit, name="edit"),
    re_path(r'^delete/(?P<id>\d+)/$', views.delete, name="delete"),
    re_path(r'^library_types/list/$', views.library_types_list, name="library_types_list"),
    re_path(r'^library_types/create/$', views.library_type_create, name="library_type_create"),
    re_path(r'^library_types/edit/(?P<id>\d+)/$', views.library_type_edit, name="library_type_edit"),
    re_path(r'^library_types/delete/(?P<id>\d+)/$', views.library_type_delete, name="library_type_delete"),

    re_path(r'^district/list/$', views.district_list, name="district_list"),
    re_path(r'^district/create/$', views.district_create, name="district_create"),
    re_path(r'^district/edit/(?P<id>\d+)/$', views.district_edit, name="district_edit"),
    re_path(r'^district/delete/(?P<id>\d+)/$', views.district_delete, name="district_delete"),
)
