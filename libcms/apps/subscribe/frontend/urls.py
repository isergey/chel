# -*- coding: utf-8 -*-
from django.conf.urls import *

from . import views


urlpatterns = (
    url(r'^$', views.index, name="index"),
    url(r'^(?P<id>[0-9]+)/$', views.subscription_detail, name="subscription_detail"),
    url(r'^journals/$', views.journals, name="journals"),
    url(r'^(?P<code>[a-z_0-9]+)/subscribe/$', views.subscribe, name="subscribe"),
    url(r'^(?P<id>[0-9]+)/unsubscribe/$', views.unsubscribe, name="unsubscribe"),
    url(r'^(?P<id>[0-9]+)/subscribe_ajax/$', views.subscribe_ajax, name="subscribe_ajax"),
    url(r'^(?P<id>[0-9]+)/unsubscribe_ajax/$', views.unsubscribe_ajax, name="unsubscribe_ajax"),
    url(r'^slr/$', views.send_letters_req, name="send_letters_req"),
    url(r'^ser/$', views.send_emails_req, name="send_emails_req"),
    url(r'^get_subscribes/$', views.get_subscribes, name="get_subscribes"),
    url(r'^set_subscribes/$', views.set_subscribes, name="set_subscribes"),
)
