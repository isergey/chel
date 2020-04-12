# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
from . import views

urlpatterns = (
    re_path(r'^admin/', include('zgate.administration.urls')),
    re_path(r'^(?P<catalog_id>\d+)/$', views.index, name="zgate_index"),
    re_path(r'^(?P<catalog_id>\d+)/order/$', views.draw_order, name="draw_order"),
    re_path(r'^(?P<catalog_id>\d+)/help/$', views.help, name="zgate_help"),

    re_path(r'^s/(?P<slug>[-_\w]+)/$', views.index, name="zgate_slug_index"),
    re_path(r'^s/(?P<slug>[-_\w]+)/order/$', views.draw_order, name="draw_order"),
    re_path(r'^s/(?P<slug>[-_\w]+)/help/$', views.help, name="zgate_slug_help"),
    re_path(r'^ss/$', views.simple_search, name="zgate_simple_search"),
    re_path(r'^requests/$', views.saved_requests_list, name="zgate_saved_requests"),
    re_path(r'^requests/go/(?P<request_id>\d+)/$', views.make_saved_request, name="zgate_make_saved_request"),
    re_path(r'^requests/delete/(?P<request_id>\d+)/$', views.delete_saved_request, name="zgate_delete_saved_request"),

    re_path(r'^documents/$', views.saved_document_list, name="zgate_saved_document_list"),
    #re_path(r'^documents/search/(?P<document_id>\d+)/$', 'search_document', name="zgate_search_saved_document"),
    re_path(r'^documents/save/$', views.save_document, name="zgate_save_document"),
    re_path(r'^documents/load/$', views.load_documents, name="zgate_load_saved_documents"),
    re_path(r'^documents/delete/(?P<document_id>\d+)/$', views.delete_saved_document, name="zgate_delete_saved_document"),
)

