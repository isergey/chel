# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('index.frontend.views',
    url(r'^$', 'index', name="index"),
)