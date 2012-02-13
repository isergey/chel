# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('users.frontend.views',
    url(r'^$', 'index', name="index"),
)