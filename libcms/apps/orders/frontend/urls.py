# -*- coding: utf-8 -*-
from django.conf.urls import re_path
from . import views
urlpatterns = (
#    re_path(r'^$', views.index , name="index"),
#    re_path(r'^(?P<id>\d+)/$', views.lib_orders, name="lib_orders"),
#    re_path(r'^zorder/(?P<library_id>\d+)/$', views.zorder, name="zorder"),
    re_path(r'^$', views.index, name="index"),
    re_path(r'^mbaorder/copy/$', views.mba_order_copy, name="mba_order_copy"),
    re_path(r'^mbaorder/reserve/$', views.mba_order_reserve, name="mba_order_reserve"),
    re_path(r'^mbaorder/delivery/$', views.mba_order_delivery, name="mba_order_delivery"),
    re_path(r'^mbaorder/org_by_code/$', views.org_by_code, name="org_by_code"),
    re_path(r'^mbaorder/make_order/$', views.make_order, name="make_order"),
    re_path(r'^mbaorder/delete/(?P<order_id>[a-z0-9]+)/$', views.delete_order, name="mba_delete_order"),
)
