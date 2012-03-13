# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.index , name="index"),
    url(r'^list/$', views.list, name="list"),
    url(r'^list/(?P<parent>\d+)/$', views.list, name="list"),
    url(r'^create/$', views.create , name="create"),
    url(r'^create/(?P<parent>\d+)/$', views.create , name="create"),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name="edit"),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name="delete"),
    url(r'^library_types/list/$', views.library_types_list, name="library_types_list"),
    url(r'^library_types/create/$', views.library_type_create, name="library_type_create"),
    url(r'^library_types/edit/(?P<id>\d+)/$', views.library_type_edit, name="library_type_edit"),
    url(r'^library_types/delete/(?P<id>\d+)/$', views.library_type_delete, name="library_type_delete"),
)
