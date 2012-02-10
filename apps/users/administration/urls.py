from django.conf.urls.defaults import *


urlpatterns = patterns('users.administration.views',
    url(r'^$', 'index', name="index"),
)