# -*- coding: utf-8 -*-
from django.urls import re_path, include

from . import views
from .administration import urls as aurls
urlpatterns = (
    re_path(r'^$', views.index , name='index'),
    re_path(r'^redirect$', views.redirect_to_url , name='redirect_to_url'),
    re_path(r'^admin/', include((aurls, 'admin'))),
)
