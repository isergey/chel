# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views

urlpatterns = (
    re_path(r'^$', views.index, name="index"),
    re_path(r'^branches/(?P<code>[/_\-0-9A-Za-z]+)/$', views.branches , name="branches"),
    re_path(r'^districts/$', views.districts , name="districts"),
    # в этом вызове id передается в GET
    re_path(r'^branches/$', views.branches , name="branches"),
    re_path(r'^detail/(?P<code>[/_\-0-9A-Za-z\s]+)/$', views.detail , name="detail"),
    re_path(r'^branches_by_district/$', views.get_branches_by_district , name="get_branches_by_district"),

)
