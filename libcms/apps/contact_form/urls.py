from django.conf.urls import re_path, include
from .frontend import urls as furls

urlpatterns = [
    #url(r'^admin/', include(aurls, namespace='administration')),
    re_path(r'^', include((furls, 'frontend'))),
]
