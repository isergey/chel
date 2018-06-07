from django.conf.urls import *
import views

urlpatterns = (
    url(r'^$', views.index, name='index'),
)
