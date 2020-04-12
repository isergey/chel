# encoding: utf-8
from django.conf.urls import re_path


from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^id/create$', views.create_id , name="create_id"),
    re_path(r'^id/(?P<id>\d+)/edit', views.edit_id , name="edit_id"),
    re_path(r'^id/(?P<id>\d+)/delete', views.delete_id , name="delete_id"),
    re_path(r'^id/list', views.id_list , name="id_list"),
    re_path(r'^id/index', views.index_important_dates , name="index_important_dates"),
#    re_path(r'^theme/create$', views.create_theme , name="create_theme"),
#    re_path(r'^theme/(?P<id>\d+)/edit', views.edit_theme , name="edit_theme"),
#    re_path(r'^theme/list', views.theme_list , name="theme_list"),

)