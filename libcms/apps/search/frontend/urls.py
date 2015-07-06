# -*- coding: utf-8 -*-
from django.conf.urls import *
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^ajax_search/$', views.ajax_search, name='ajax_search'),
    url(r'^ajax_facets/$', views.ajax_facets, name='ajax_facets'),
    url(r'^ajax_detail/$', views.ajax_detail, name='ajax_detail'),
    url(r'^facets/$', views.facets, name='facets'),
    # url(r'^facets/more/$', views.more_facets, name='more_facets'),
    url(r'^facets/more/explore/$', views.facet_explore, name='facet_explore'),
    url(r'^deatil/$', views.detail, name='detail'),
    url(r'^requests/$', views.saved_search_requests, name='saved_search_requests'),
    url(r'^requests/save/$', views.save_search_request, name='save_search_request'),
    url(r'^requests/delete/(?P<id>\d+)/$', views.delete_search_request, name='delete_search_request'),
)

