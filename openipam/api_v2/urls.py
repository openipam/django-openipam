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
router.register(r"networks", views.network.NetworkViewSet)
router.register(r"pools", views.network.AddressPoolViewSet)
router.register(r"dhcp-groups", views.network.DhcpGroupViewSet)

# TODO: figure out how to get CSRF protection working with the new API
urlpatterns = [
    path("", include(router.urls)),
    path("admin/logs/", csrf_exempt(views.admin.LogEntryList.as_view())),
    path("admin/email-logs/", csrf_exempt(views.admin.EmailLogsList.as_view())),
    path(
        "user/",
        csrf_exempt(views.user.UserView.as_view()),
    ),
]
