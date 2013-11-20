from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

import autocomplete_light


autocomplete_light.autodiscover()

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # openIPAM urls
    url(r'^', include('openipam.core.urls')),

    # Admin Frontend
    url(r'^', include(admin.site.urls)),

    # Utitity routes to serve admin
    url(r'^admin_tools/', include('admin_tools.urls')),
)

# Serve Static and Media on development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
