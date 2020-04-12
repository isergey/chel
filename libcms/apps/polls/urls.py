# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^admin/', include(('polls.administration.urls', 'administration'))),
    re_path(r'^', include(('polls.frontend.urls', 'frontend'))),

)

