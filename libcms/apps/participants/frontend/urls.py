# -*- coding: utf-8 -*-
from django.conf.urls import *
import views
urlpatterns = patterns(views,
    url(r'^$', views.districts, name="index"),
    url(r'^branches/(?P<code>[/_\-0-9A-Za-z]+)/$', views.branches , name="branches"),
    url(r'^districts/$', views.districts , name="districts"),
    # в этом вызове id передается в GET
    url(r'^branches/$', views.branches , name="branches"),
    url(r'^detail/(?P<code>[/_\-0-9A-Za-z\s]+)/$', views.detail , name="detail"),
    url(r'^branches_by_district/$', views.get_branches_by_district , name="get_branches_by_district"),

)
