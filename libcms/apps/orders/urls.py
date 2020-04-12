# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^', include(('orders.frontend.urls', 'frontend'))),
    #    (r'^admin/', include('urt.administration.urls', namespace='administration')),
)

