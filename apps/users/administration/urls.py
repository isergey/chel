# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('users.administration.views',
    url(r'^$', 'index', name="index"),
    url(r'^users$', 'users', name="users"),
)