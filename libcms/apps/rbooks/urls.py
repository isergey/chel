# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('',
    # (r'^admin/', include('news.administration.urls', namespace='administration')),
    (r'^', include('rbooks.frontend.urls', namespace='frontend')),

)

