# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from django.views.generic import TemplateView
from . import views

urlpatterns = (
    re_path(r'^$',TemplateView.as_view(template_name='ssearch/statistics/index.html'), name='index'),
    re_path(r'^incomes/$',TemplateView.as_view(template_name='ssearch/statistics/incomes.html'), name='incomes'),
    re_path(r'^actions/$', TemplateView.as_view(template_name='ssearch/statistics/actions.html'), name='actions'),
    re_path(r'^users/$', TemplateView.as_view(template_name='ssearch/statistics/users.html'), name='users'),
    re_path(r'^materials/$', TemplateView.as_view(template_name='ssearch/statistics/materials.html'), name='materials'),
    re_path(r'^search/$', TemplateView.as_view(template_name='ssearch/statistics/search.html'), name='search'),
    re_path(r'^popular/$', views.popular_records_stat, name='popular'),
    re_path(r'^incomes_stat/$', views.incomes_stat, name='incomes_stat'),
    re_path(r'^actions_stat/$', views.actions_stat, name='actions_stat'),
    re_path(r'^users_stat/$', views.users_stat, name='users_stat'),
    re_path(r'^material_types_stat/$', views.material_types_stat, name='material_types_stat'),
    re_path(r'^search_requests_stat/$', views.search_requests_stat, name='search_requests_stat'),
)