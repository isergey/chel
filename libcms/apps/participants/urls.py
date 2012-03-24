# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

#from participants.api.views import auth_user

urlpatterns = patterns('',
#    (r'^', include('pages.frontend.urls', namespace='frontend')),
    (r'^admin/', include('participants.administration.urls', namespace='administration')),
)



#urlpatterns = patterns('participants.views',
#    url(r'^$', 'index', name="participants_index"),
#    url(r'^detail/(?P<code>[a-zA-Z\d]+)/$', 'detail', name="participants_detail"),
#
#    url(r'^districts/detail/(?P<code>[a-zA-Z\d]+)/$', 'detail_by_district', name="participants_detail_by_district"),
#    url(r'^districts/$', 'districts', name="participants_districts"),
#    url(r'^districts/(?P<id>\d+)/$', 'by_district', name="participants_by_district"),
#    url(r'^xml/$', 'xml_dump', name="participants_xml_dump"),
#    url(r'^json/bydistrict/$', 'by_district_json', name="participants_json_by_district"),
#)
#
##api urls
#urlpatterns += patterns('participants.api.views',
#    url(r'^api/auth_user/$', 'auth_user', name="participants_api_auth_user"),
#    url(r'^api/get_user_orgs/$', 'get_user_orgs', name="participants_api_get_user_orgs"),
#    url(r'^api/get_org/$', 'get_org', name="participants_api_get_org"),
#    url(r'^api/find_orgs/$', 'find_orgs', name="participants_api_find_orgs"),
#    url(r'^api/get_user/$', 'get_user', name="participants_api_get_user"),
#)
#
