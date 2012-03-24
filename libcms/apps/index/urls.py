# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^', include('index.frontend.urls', namespace='frontend')),
    (r'^admin/', include('index.administration.urls', namespace='administration')),
)

