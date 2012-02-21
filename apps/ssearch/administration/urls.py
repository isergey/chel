# coding: utf-8
from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^$', views.initial, name='initial'),
    url(r'^upload/$', views.upload, name="upload"),
    url(r'^process/$', views.pocess, name="process"),
)