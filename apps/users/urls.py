# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^', include('users.frontend.urls', namespace='frontend')),
    (r'^admin/', include('users.administration.urls', namespace='administration')),
)

