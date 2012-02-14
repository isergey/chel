# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('accounts.administration.views',
    url(r'^$', 'index', name="index"),
    url(r'^users$', 'users_list', name="users_list"),
    url(r'^users/edit/(?P<id>\d+)/$', 'edit_user', name="edit_user"),
    url(r'^groups', 'groups_list', name="groups_list"),
)