# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
from .frontend import urls as furls
from .administration import urls as aurls
from .api import urls as api_urls

urlpatterns = (
    re_path(r'^admin/', include((aurls, 'administration'))),
    re_path(r'^api/', include((api_urls, 'api'))),
    re_path(r'^', include((furls, 'frontend'))),
)
