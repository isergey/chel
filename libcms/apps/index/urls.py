# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^', include(('index.frontend.urls', 'frontend'))),
    re_path(r'^admin/', include(('index.administration.urls', 'administration'))),
)

