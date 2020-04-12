# -*- encoding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^albums/$', views.albums_list, name="albums_list"),
    re_path(r'^albums/images/(?P<id>\d+)/$', views.album_view, name="album_view"),
    re_path(r'^albums/upload/(?P<id>\d+)/$', views.album_upload, name="album_upload"),
    re_path(r'^albums/create/$', views.album_create, name="album_create"),
    re_path(r'^albums/edit/(?P<id>\d+)/$', views.album_edit, name="album_edit"),
    re_path(r'^albums/delete/(?P<id>\d+)/$', views.album_delete, name="album_delete"),

    re_path(r'^albums/images/edit/(?P<id>\d+)/$', views.image_edit, name="image_edit"),
    re_path(r'^albums/images/delete/(?P<id>\d+)/$', views.image_delete, name="image_delete"),
#    re_path(r'^news/create/$', views.create_news , name="create_news"),
#    re_path(r'^news/edit/(?P<id>\d+)/$', views.edit_news, name="edit_news"),
#    re_path(r'^news/delete/(?P<id>\d+)/$', views.delete_news, name="delete_news"),
)