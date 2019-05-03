from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from autocomplete_light import shortcuts as al

from openipam.core.views import server_error, page_not_found

al.autodiscover()

admin.autodiscover()

urlpatterns = [
    # Testing 404 and 500 pages
    url(r"^500/$", server_error),
    url(r"^404/$", page_not_found),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    # openIPAM urls
    url(r"^", include("openipam.core.urls")),
    # Admin Frontend
    url(r"^", include(admin.site.urls)),
    # Utitity routes to serve admin
    url(r"^admin_tools/", include("admin_tools.urls")),
]

# Serve Static and Media on development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG is False:  # if DEBUG is True it will be served automatically
    urlpatterns += [
        url(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT})
    ]
else:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
    urlpatterns += staticfiles_urlpatterns()

handler403 = "openipam.core.views.page_denied"
handler404 = "openipam.core.views.page_not_found"
handler500 = "openipam.core.views.server_error"
