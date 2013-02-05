# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('',
    (r'^admin/', include('pages.administration.urls', namespace='administration')),
    (r'^stat/', include('pages.stat.urls', namespace='stat')),
    (r'^', include('pages.frontend.urls', namespace='frontend')),

)

