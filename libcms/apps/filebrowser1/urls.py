# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include


urlpatterns = (
    re_path(r'^admin/', include(('filebrowser.administration.urls', 'administration'))),
)

