# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('',
    (r'^admin/', include('gallery.administration.urls', namespace='administration')),
#    (r'^', include('gallery.frontend.urls', namespace='frontend')),

)

