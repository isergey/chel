# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    # (r'^indexer/', include('ssearch.indexer.urls', namespace='indexer')),
    re_path(r'^', include(('ssearch.frontend.urls', 'frontend'))),
    re_path(r'^statistics/', include(('ssearch.statistics.urls', 'statistics'))),
    re_path(r'^sitemap/', include(('ssearch.sitemap.urls', 'sitemap'))),
)
