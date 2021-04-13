# -*- coding: utf-8 -*-
from django.conf import settings

from django.conf.urls.static import static
from django.conf.urls import include,re_path
from django.contrib.admin.sites import site
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.conf.urls.i18n import i18n_patterns

urlpatterns = []

urlpatterns += i18n_patterns(
    re_path(r'^', include(('index.urls', 'index'))),
    re_path(r'^auth/', include('django.contrib.auth.urls')),
    re_path(r'^robots.txt', include('robots_txt.urls')),
    re_path(r'^sitemap/', include(('sitemap.urls', 'sitemap'))),
    re_path(r'^core/', include(('core.urls', 'core'))),
    re_path(r'^accounts/', include(('accounts.urls', 'accounts'))),
    re_path(r'^filebrowser/', include(('filebrowser.urls', 'filebrowser'))),
    re_path(r'^menu/', include(('menu.urls', 'menu'))),
    re_path(r'^pages/', include(('pages.urls', 'pages'))),
    re_path(r'^news/', include(('news.urls', 'news'))),
    re_path(r'^events/', include(('events.urls', 'events'))),
    re_path(r'^professionals/pages/', include(('professionals_pages.urls', 'professionals_pages'))),
    re_path(r'^professionals/news/', include(('professionals_news.urls', 'professionals_news'))),
    re_path(r'^professionals/', include(('professionals.urls', 'professionals'))),
    re_path(r'^participants/(?P<code>[_\-0-9A-Za-z]+)/pages/', include(('participants_pages.urls', 'participants_pages'))),
    re_path(r'^participants/', include(('participants.urls', 'participants'))),
    re_path(r'^forum/', include(('forum.urls', 'forum'))),
    re_path(r'^orders/', include(('orders.urls', 'orders'))),
    #re_path(r'^rbooks/', include(('rbooks.urls', 'rbooks'))),
    #re_path(r'^zgate/', include(('zgate.urls'))),
    re_path(r'^ask_librarian/', include(('ask_librarian.urls', 'ask_librarian'))),
    re_path(r'^gallery/', include(('gallery.urls', 'gallery'))),
    re_path(r'^guestbook/', include(('guestbook.urls', 'guestbook'))),
    re_path(r'^polls/', include(('polls.urls', 'polls'))),
    re_path(r'^cid/', include(('cid.urls', 'cid'))),
    re_path(r'^ssearch/', include(('ssearch.urls', 'ssearch'))),
    #re_path(r'^search/', include(('search.urls', 'search'))),
    re_path(r'^harvester/', include(('harvester.urls', 'harvester'))),
    # Uncomment the next line to enable the admin:
    re_path(r'^radmin/', admin.site.urls),
    re_path(r'^jsi18n/$', site.i18n_javascript, name='jsi18n'),
    # url(r'^sauth/', include('social_auth.urls')),
    # re_path(r'^captcha/', include('captcha.urls')),
    re_path(r'^contact_form/', include(('contact_form.urls', 'contact_form'))),
    re_path(r'^subscribe/', include(('subscribe.urls', 'subscribe'))),
    re_path(r'^opac/', include(('sso_opac.urls', 'sso_opac'))),
    # url(r'^sql/', include('explorer.urls')),
)

urlpatterns += (
    re_path(r'^dl/', include(('rbooks.urls', 'rbooks'))),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)