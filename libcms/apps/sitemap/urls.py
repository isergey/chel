# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
from .frontend import urls as furls
urlpatterns = (
    re_path(r'^', include((furls, 'frontend'))),

)

