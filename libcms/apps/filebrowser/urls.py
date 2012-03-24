# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^admin/', include('filebrowser.administration.urls', namespace='administration')),
)

