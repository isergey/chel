# -*- coding: utf-8 -*-
from django.conf.urls import *
from .administration import urls

urlpatterns = (
    url(r'^admin/', include((urls, 'administration'))),
)

