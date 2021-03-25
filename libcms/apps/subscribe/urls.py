# -*- coding: utf-8 -*-
from django.conf.urls import *
from .frontend import urls as furls
from .administration import urls as aurls


urlpatterns = (
    url(r'^admin/', include((aurls, 'administration'))),
    url(r'^', include((furls, 'frontend'))),
)

