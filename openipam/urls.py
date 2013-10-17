from django.conf.urls import patterns, include, url
from django.contrib import admin
import autocomplete_light


autocomplete_light.autodiscover()

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Utitity routes to serve admin
    url(r'^admin_tools/', include('admin_tools.urls')),

    # Admin Frontend
    url(r'^admin/', include(admin.site.urls)),

    # openIPAM urls
    url(r'^', include('openipam.core.urls')),
)
