# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('',
    # (r'^indexer/', include('ssearch.indexer.urls', namespace='indexer')),
    (r'^', include('ssearch.frontend.urls', namespace='frontend')),

)

