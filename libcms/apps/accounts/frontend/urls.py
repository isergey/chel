# -*- coding: utf-8 -*-
from django.conf.urls import re_path, include
#from django.contrib.auth.views import  login, logout, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
# from  views import done, error, home
from django.contrib.auth.views import LoginView, LogoutView

LoginView.template_name = 'accounts/frontend/login.html'


from . import views
urlpatterns = [
    re_path(r'^$', views.index, name="index"),
    re_path(r'^registration/$', views.registration, name="registration"),
    re_path(r'^confirm/(?P<hash>[a-h0-9]{1,32})/$', views.confirm_registration, name="confirm_registration"),
    re_path(r'^login/$', LoginView.as_view(), name="login"),
    re_path(r'^logout/$', LogoutView.as_view(), name="logout"),
]

# urlpatterns += [
#
#     re_path(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/frontend/login.html'}, name='login'),
#     re_path(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
#     re_path(r'^password/change/$', 'django.contrib.auth.views.password_change', name='password_change'),
#     re_path(r'^password/change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
#     re_path(r'^password/reset/$', 'django.contrib.auth.views.password_reset',
#         {
#             'template_name': 'accounts/frontend/registration/password_reset_form.html',
#             'email_template_name': 'accounts/frontend/registration/password_reset_email.html',
#             'post_reset_redirect': 'accounts/password/reset/done/'
#         },
#         name='password_reset'
#     ),
#     re_path(r'^password/reset/done/$',
#         'django.contrib.auth.views.password_reset_done',
#         {
#             'template_name': 'accounts/frontend/registration/password_reset_done.html',
#         },
#         name='password_reset_done'
#     ),
#     re_path(r'^password/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
#         'django.contrib.auth.views.password_reset_confirm',
#         {
#             'template_name': 'accounts/frontend/registration/password_reset_confirm.html',
#             'post_reset_redirect': '/accounts/password/reset/complete/'
#         },
#         name='password_reset_confirm'
#     ),
#     re_path(r'^password/reset/complete/$',
#         'django.contrib.auth.views.password_reset_complete',
#         {
#             'template_name': 'accounts/frontend/registration/password_reset_complete.html',
#         },
#         name='password_reset_complete'),
# )

# urlpatterns += patterns('',
#     url(r'^$', home, name='home'),
#     url(r'^login/done/$', done, name='done'),
#     url(r'^login/error/$', error, name='error'),
# )