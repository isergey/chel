# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.index , name="index"),
    url(r'^pages/$', views.pages_list, name="pages_list"),
    url(r'^pages/(?P<parent>\d+)/$', views.pages_list, name="pages_list"),
    url(r'^pages/create/$', views.create_page , name="create_page"),
    url(r'^pages/edit/(?P<id>\d+)/$', views.edit_page, name="edit_page"),
)