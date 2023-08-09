from django.urls import include, path

from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from . import views
from .views import misc


router = routers.DefaultRouter()
router.register(r"hosts", views.hosts.HostViewSet)
router.register(r"dns", views.dns.DnsViewSet)
router.register(r"domains", views.dns.DomainViewSet)
router.register(r"attributes", misc.AttributeViewSet)

# TODO: figure out how to get CSRF protection working with the new API
urlpatterns = [
    path("", include(router.urls)),
    path("admin/logs/", csrf_exempt(views.admin.LogEntryList.as_view())),
    path("admin/email-logs/", csrf_exempt(views.admin.EmailLogsList.as_view())),
    path(
        "dns-types/",
        csrf_exempt(views.dns.DnsTypeList.as_view()),
        name="api_dns_type_list",
    ),
    path(
        "dns-views/",
        csrf_exempt(views.dns.DnsViewsList.as_view()),
        name="api_dns_view_list",
    ),
    path(
        "dhcp-dns/",
        csrf_exempt(views.dns.DhcpDnsRecordsList.as_view()),
        name="api_dhcp_dns_list",
    ),
    path(
        "user/",
        csrf_exempt(views.user.UserView.as_view()),
    ),
]
