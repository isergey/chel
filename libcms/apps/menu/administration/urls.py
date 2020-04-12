# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^menu/$', views.menu_list, name="menu_list"),
    re_path(r'^menu/create/$', views.create_menu , name="create_menu"),
    re_path(r'^menu/edit/(?P<id>\d+)/$', views.edit_menu, name="edit_menu"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/$', views.item_list, name="item_list"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/create/$', views.create_item, name="item_create"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/(?P<parent>\d+)/create/$', views.create_item, name="item_create"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/edit/(?P<id>\d+)/$', views.item_edit, name="item_edit"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/delete/(?P<id>\d+)/$', views.item_delete, name="item_delete"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/up/(?P<id>\d+)/$', views.item_up, name="item_up"),
    re_path(r'^menu/(?P<menu_id>\d+)/items/down/(?P<id>\d+)/$', views.item_down, name="item_down"),
#    url(r'^pages/(?P<parent>\d+)/$', views.pages_list, name="pages_list"),
#    url(r'^pages/create/$', views.create_page , name="create_page"),
#    url(r'^pages/create/(?P<parent>\d+)/$', views.create_page , name="create_page"),
#    url(r'^pages/edit/(?P<id>\d+)/$', views.edit_page, name="edit_page"),
#    url(r'^pages/delete/(?P<id>\d+)/$', views.delete_page, name="delete_page"),
#    url(r'^pages/content/create/(?P<page_id>\d+)/$', views.create_page_content, name="create_page_content"),
#    url(r'^pages/content/edit/(?P<page_id>\d+)/(?P<lang>[a-z]{2})$', views.edit_page_content, name="edit_page_content"),
)