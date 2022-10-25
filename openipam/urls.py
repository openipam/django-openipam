from django.conf.urls import include
from django.urls import path, re_path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from openipam.core.views import server_error, page_not_found, bad_request, page_denied

admin.autodiscover()

urlpatterns = [
    # Testing 404 and 500 pages
    path("500/", server_error),
    path("404/", page_not_found),
    path("403/", page_denied),
    path("400/", bad_request),
    # Uncomment the admin/doc line below to enable admin documentation:
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # openIPAM urls
    path("", include("openipam.core.urls")),
    # Admin Frontend
    path("", admin.site.urls),
    # Utitity routes to serve admin
    path("admin_tools/", include("admin_tools.urls")),
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
