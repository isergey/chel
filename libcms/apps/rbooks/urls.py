# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
#    (r'^admin/', include('rbooks.administration.urls', namespace='administration')),
    re_path(r'^', include(('rbooks.frontend.urls', 'frontend'))),

)

