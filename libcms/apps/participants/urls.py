# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include


urlpatterns = (
    re_path(r'^api/', include(('participants.api.urls', 'api'))),
    re_path(r'^admin/', include(('participants.administration.urls', 'administration'))),
    re_path(r'^', include(('participants.frontend.urls', 'frontend'))),
)


