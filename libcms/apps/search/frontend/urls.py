# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name='index'),
    re_path(r'^ajax_search/$', views.ajax_search, name='ajax_search'),
    re_path(r'^ajax_facets/$', views.ajax_facets, name='ajax_facets'),
    re_path(r'^ajax_detail/$', views.ajax_detail, name='ajax_detail'),
    re_path(r'^facets/$', views.facets, name='facets'),
    # re_path(r'^facets/more/$', views.more_facets, name='more_facets'),
    re_path(r'^facets/more/explore/$', views.facet_explore, name='facet_explore'),
    re_path(r'^deatil/$', views.detail, name='detail'),
    re_path(r'^requests/$', views.saved_search_requests, name='saved_search_requests'),
    re_path(r'^requests/save/$', views.save_search_request, name='save_search_request'),
    re_path(r'^requests/delete/(?P<id>\d+)/$', views.delete_search_request, name='delete_search_request'),
)

