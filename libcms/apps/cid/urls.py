# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('',
    (r'^admin/', include('cid.administration.urls', namespace='administration')),
    (r'^', include('cid.frontend.urls', namespace='frontend')),

)

