# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^admin/', include('news.administration.urls', namespace='administration')),
#    (r'^', include('menu.frontend.urls', namespace='frontend')),

)

