from django.conf.urls import *
import views

urlpatterns = patterns(views,
    url(r'^$', views.index , name="index"),
    url(r'^edoc/$', views.edoc , name="edoc"),
    url(r'^key/$', views.key , name="key"),
    url(r'^edoc_stream/$', views.edoc_stream , name="edoc_stream"),
)
