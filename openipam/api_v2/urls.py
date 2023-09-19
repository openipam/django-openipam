from django.urls import include, path

from rest_framework import routers
from . import views
from .views import misc


router = routers.DefaultRouter()
router.register(r"hosts", views.hosts.HostViewSet)
router.register(r"dns", views.dns.DnsViewSet)
router.register(r"dhcp", views.dns.DhcpDnsViewSet)
router.register(r"domains", views.dns.DomainViewSet)
router.register(r"attributes", misc.AttributeViewSet)
router.register(r"networks", views.network.NetworkViewSet)
router.register(r"pools", views.network.AddressPoolViewSet)
router.register(r"dhcp-groups", views.network.DhcpGroupViewSet)
router.register(r"users", views.users.UserViewSet)
router.register(r"addresses", views.network.AddressViewSet)
router.register(r"address-types", views.network.AddressTypeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/logs/", views.admin.LogEntryList.as_view()),
    path("admin/email-logs/", views.admin.EmailLogsList.as_view()),
    path("admin/stats/", misc.DashboardAPIView.as_view()),
    path("groups/", views.users.GroupView.as_view()),
]
