# -*- coding: utf-8 -*-
from django.conf.urls import *
from . import views

urlpatterns = (
    url(r'^$', views.index, name='index'),
    url(r'^d$', views.detail_tpl, name='detail_tpl'),
    url(r'^search$', views.search, name='search'),
    url(r'^ui_config$', views.ui_config, name='ui_config'),
    url(r'^facets$', views.facets, name='facets'),
    url(r'^facet$', views.facet, name='facet'),
    url(r'^detail$', views.detail, name='detail'),
    url(r'^record_dump', views.record_dump, name='record_dump'),
    url(r'^mlt$', views.more_like_this, name='more_like_this'),
    url(r'^linked_records', views.linked_records, name='linked_records'),
    url(r'^related_issues', views.related_issues, name='related_issues'),
    url(r'^statistics$', views.statistics, name='statistics'),
    url(r'^save_request', views.save_request, name='save_request'),
)

