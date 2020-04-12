# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include

urlpatterns = (
    re_path(r'^admin/', include(('ask_librarian.administration.urls', 'administration'))),
    re_path(r'^', include(('ask_librarian.frontend.urls', 'frontend'))),

)

