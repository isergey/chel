# -*- coding: utf-8 -*-
from django.conf.urls import *
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name="index"),
    url(r'^detail$', views.detail, name="detail"),
    url(r'^m_f$', views.more_facet, name="more_facet"),
    url(r'^m_sf$', views.more_subfacet, name="more_subfacet"),
    url(r'^test_solr_request$', views.test_solr_request, name="test_solr_request"),
)