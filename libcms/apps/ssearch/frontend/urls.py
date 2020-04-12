# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^detail$', views.detail, name="detail"),
    re_path(r'^log$', views.log, name="log"),
    re_path(r'^m_f$', views.more_facet, name="more_facet"),
    re_path(r'^m_sf$', views.more_subfacet, name="more_subfacet"),
    re_path(r'^test_solr_request$', views.test_solr_request, name="test_solr_request"),
)