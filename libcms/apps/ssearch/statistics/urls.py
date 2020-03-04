# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.views.generic import TemplateView
import views

urlpatterns = patterns('',
    url(r'^$',TemplateView.as_view(template_name='ssearch/statistics/index.html'), name="incomes"),
    url(r'^incomes/$',TemplateView.as_view(template_name='ssearch/statistics/incomes.html'), name="incomes"),
    url(r'^actions/$', TemplateView.as_view(template_name='ssearch/statistics/actions.html'), name="actions"),
    url(r'^users/$', TemplateView.as_view(template_name='ssearch/statistics/users.html'), name="users"),
    url(r'^incomes_stat$', views.incomes_stat, name="incomes_stat"),
    url(r'^actions_stat$', views.actions_stat, name="actions_stat"),
    url(r'^users_stat$', views.users_stat, name="users_stat"),
)