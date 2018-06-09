# encoding: utf-8
from django.conf.urls import *


import views

urlpatterns = patterns('',
    url(r'^$', views.index , name="index"),
    url(r'^id/create$', views.create_id , name="create_id"),
    url(r'^id/(?P<id>\d+)/edit', views.edit_id , name="edit_id"),
    url(r'^id/(?P<id>\d+)/delete', views.delete_id , name="delete_id"),
    url(r'^id/list', views.id_list , name="id_list"),
    url(r'^id/index', views.index_important_dates , name="index_important_dates"),
#    url(r'^theme/create$', views.create_theme , name="create_theme"),
#    url(r'^theme/(?P<id>\d+)/edit', views.edit_theme , name="edit_theme"),
#    url(r'^theme/list', views.theme_list , name="theme_list"),

)