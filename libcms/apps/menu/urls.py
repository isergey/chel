# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^admin/', include(('menu.administration.urls', 'administration'))),
#    (r'^', include('menu.frontend.urls', namespace='frontend')),

)

