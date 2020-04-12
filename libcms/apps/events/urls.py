# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
from .frontend import urls as furls
from .administration import urls as aurls

urlpatterns = (
    re_path(r'^admin/', include((aurls, 'administration'))),
    re_path(r'^', include((furls, 'frontend'))),
)
