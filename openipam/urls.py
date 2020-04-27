from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from openipam.core.views import server_error, page_not_found, bad_request, page_denied

from autocomplete_light import shortcuts as al

al.autodiscover()

admin.autodiscover()

urlpatterns = [
    # Testing 404 and 500 pages
    path("500/", server_error),
    path("404/", page_not_found),
    path("403/", page_denied),
    path("400/", bad_request),
    # Uncomment the admin/doc line below to enable admin documentation:
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # API
    path("api/", include("openipam.api.urls")),
    # Autocomplete
    path("ac/", include("autocomplete_light.urls")),
    path("select2/", include("django_select2.urls")),
    # Hosts
    path("hosts/", include("openipam.hosts.urls")),
    # DNS
    path("dns/", include("openipam.dns.urls")),
    # USU Reports and Tools
    path("reports/", include("openipam.report.urls")),
    # Core
    path("", include("openipam.core.urls")),
    # User
    path("", include("openipam.user.urls")),
    # Admin
    path("", admin.site.urls),
]

# Serve Static and Media on development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG is False:  # if DEBUG is True it will be served automatically
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}
        )
    ]
else:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += staticfiles_urlpatterns()

handler400 = "openipam.core.views.bad_request"
handler403 = "openipam.core.views.page_denied"
handler404 = "openipam.core.views.page_not_found"
handler500 = "openipam.core.views.server_error"
