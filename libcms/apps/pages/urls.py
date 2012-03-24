# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^admin/', include('pages.administration.urls', namespace='administration')),
    (r'^', include('pages.frontend.urls', namespace='frontend')),

)

