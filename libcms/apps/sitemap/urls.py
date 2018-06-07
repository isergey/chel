# -*- coding: utf-8 -*-
from django.conf.urls import *
from .frontend import urls as furls
urlpatterns = (
    url(r'^', include(furls, namespace='frontend')),

)

