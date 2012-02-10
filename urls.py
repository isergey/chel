from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^core/', include('core.urls', namespace='core')),
    (r'^users/', include('users.urls', namespace='users')),
    (r'^ask_librarian/', include('ask_librarian.urls', namespace='ask_librarian')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
