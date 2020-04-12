# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^', include(('forum.frontend.urls', 'frontend'))),
    #    (r'^admin/', include('forum.administration.urls', namespace='administration')),
)
