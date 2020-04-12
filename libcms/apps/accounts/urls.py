# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^', include(('accounts.frontend.urls', 'frontend'))),
    re_path(r'^admin/', include(('accounts.administration.urls', 'administration'))),
)

