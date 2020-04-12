# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^admin/', include(('gallery.administration.urls', 'administration'))),
    re_path(r'^', include(('gallery.frontend.urls', 'frontend'))),

)

