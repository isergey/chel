# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^admin/', include(('pages.administration.urls', 'administration'))),
    re_path(r'^stat/', include(('pages.stat.urls', 'stat'))),
    re_path(r'^', include(('pages.frontend.urls', 'frontend'))),

)

