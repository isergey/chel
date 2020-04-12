# -*- coding: utf-8 -*-
from django.conf.urls import re_path

from . import views

urlpatterns = (
    re_path(r'^$', views.index , name="index"),
    re_path(r'^categories/$', views.categories_list, name="categories_list"),
    re_path(r'^categories/create/$', views.category_create, name="category_create"),
    re_path(r'^categories/(?P<parent>\d+)/create/$', views.category_create, name="category_create"),
    re_path(r'^categories/edit/(?P<id>\d+)/$', views.category_edit, name="category_edit"),
    re_path(r'^categories/delete/(?P<id>\d+)/$', views.category_delete, name="category_delete"),
    re_path(r'^categories/up/(?P<id>\d+)/$', views.category_up, name="category_up"),
    re_path(r'^categories/down/(?P<id>\d+)/$', views.category_down, name="category_down"),

    re_path(r'^questions/$', views.questions_list, name="questions_list"),
    re_path(r'^processes/my/$', views.questions_list, name="questions_processes", kwargs={'my':True}),
    re_path(r'^questions/question_answer/(?P<id>\d+)/$', views.question_answer, name="question_answer"),
    re_path(r'^questions/to_process/(?P<id>\d+)/$', views.questions_to_process, name="questions_to_process"),
    re_path(r'^questions/detail/(?P<id>\d+)/$', views.question_detail, name="question_detail"),
    re_path(r'^questions/edit/(?P<id>\d+)/$', views.question_edit, name="question_edit"),
    re_path(r'^questions/delete/(?P<id>\d+)/$', views.question_delete, name="question_delete"),

#    re_path(r'^categories/up/(?P<id>\d+)/$', views.category_up, name="category_up"),
#    re_path(r'^categories/down/(?P<id>\d+)/$', views.category_down, name="category_down"),
#    re_path(r'^pages/(?P<parent>\d+)/$', views.pages_list, name="pages_list"),
#    re_path(r'^pages/create/$', views.create_page , name="create_page"),
#    re_path(r'^pages/create/(?P<parent>\d+)/$', views.create_page , name="create_page"),
#    re_path(r'^pages/edit/(?P<id>\d+)/$', views.edit_page, name="edit_page"),
#    re_path(r'^pages/delete/(?P<id>\d+)/$', views.delete_page, name="delete_page"),
#    re_path(r'^pages/content/create/(?P<page_id>\d+)/$', views.create_page_content, name="create_page_content"),
#    re_path(r'^pages/content/edit/(?P<page_id>\d+)/(?P<lang>[a-z]{2})$', views.edit_page_content, name="edit_page_content"),
)