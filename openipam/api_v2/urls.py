from django.urls import include, path
# from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"hosts", views.hosts.HostViewSet)
router.register(r"dns", views.dns.DnsViewSet)
router.register(r"domains", views.dns.DomainViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
