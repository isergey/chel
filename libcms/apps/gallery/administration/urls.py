# -*- encoding: utf-8 -*-
from django.conf.urls import *

import views

urlpatterns = patterns('',
    url(r'^$', views.index , name="index"),
    url(r'^albums/$', views.albums_list, name="albums_list"),
    url(r'^albums/images/(?P<id>\d+)/$', views.album_view, name="album_view"),
    url(r'^albums/upload/(?P<id>\d+)/$', views.album_upload, name="album_upload"),
    url(r'^albums/create/$', views.album_create, name="album_create"),
    url(r'^albums/edit/(?P<id>\d+)/$', views.album_edit, name="album_edit"),
    url(r'^albums/delete/(?P<id>\d+)/$', views.album_delete, name="album_delete"),

    url(r'^albums/images/edit/(?P<id>\d+)/$', views.image_edit, name="image_edit"),
    url(r'^albums/images/delete/(?P<id>\d+)/$', views.image_delete, name="image_delete"),
#    url(r'^news/create/$', views.create_news , name="create_news"),
#    url(r'^news/edit/(?P<id>\d+)/$', views.edit_news, name="edit_news"),
#    url(r'^news/delete/(?P<id>\d+)/$', views.delete_news, name="delete_news"),
)