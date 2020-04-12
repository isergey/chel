# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^', include(('professionals.frontend.urls', 'frontend'))),
)
