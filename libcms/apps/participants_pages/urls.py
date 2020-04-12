# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^admin/', include(('participants_pages.administration.urls', 'administration'))),
    re_path(r'^', include(('participants_pages.frontend.urls', 'frontend'))),
)

