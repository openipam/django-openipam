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
    path('dns-types/', views.dns.DnsTypeList.as_view(), name='api_dns_type_list'),
    path('dns-views/', views.dns.DnsViewsList.as_view(), name='api_dns_view_list'),
    path('dhcp-dns/', views.dns.DhcpDnsRecordsList.as_view(), name='api_dhcp_dns_list'),
    path('domains/<name>/', views.dns.DomainViewSet.as_view({'get': 'retrieve',
                                                             'patch': 'partial_update',
                                                             'delete': 'destroy',
                                                             'post': 'add_dns_record'}), name='api_domain_dns_list'),
]
