# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
from . import views

urlpatterns = (
#    (r'^admin/', include('rbooks.administration.urls', namespace='administration')),
    re_path(r'^$', views.index, name='index'),
    re_path(r'^on_hand$', views.on_hand, name='on_hand'),
    re_path(r'^renewal$', views.renewal, name='renewal'),
    re_path(r'^incomes$', views.incomes, name='incomes'),
)

