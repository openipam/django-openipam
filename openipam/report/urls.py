from django.urls import path

from openipam.report import views

app_name = "report"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("leases/usage/", views.LeaseUsageView.as_view(), name="lease_usage"),
    path("weathermap/", views.WeatherMapView.as_view(), name="weather_map"),
    path("buildingmap/", views.BuildingMapView.as_view(), name="building_map"),
    path("disabled/", views.DisabledHostsView.as_view(), name="disabled"),
    path("server_hosts/", views.ServerHostsView.as_view(), name="server_hosts"),
    path("host_dns/", views.HostDNSView.as_view(), name="host_dns"),
    path("ptr_dns/", views.PTRDNSView.as_view(), name="ptr_dns"),
]
