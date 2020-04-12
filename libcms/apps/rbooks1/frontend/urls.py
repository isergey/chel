from django.conf.urls import *
from . import views

urlpatterns = patterns(views,
    url(r'^$', views.index , name="index"),
    url(r'^edoc/$', views.edoc , name="edoc"),
    url(r'^key/$', views.key , name="key"),
    url(r'^pic/$', views.picture , name="picture"),
    url(r'^edoc_stream/$', views.edoc_stream , name="edoc_stream"),
)
