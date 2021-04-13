# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
from . import views

urlpatterns = (
#    (r'^admin/', include('rbooks.administration.urls', namespace='administration')),
    re_path(r'^', views.index, name='index'),

)

