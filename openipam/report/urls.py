from django.conf.urls import url

from openipam.report import views


urlpatterns = [
    url(r'^leases/usage/$', views.LeaseUsageView.as_view(), name='reports_lease_usage'),
    url(r'^weathermap/$', views.WeatherMapView.as_view(), name='reports_weather_map'),
    url(r'^disabled/$', views.DisabledHostsView.as_view(), name='reports_disabled'),
    url(r'^server_hosts/$', views.ServerHostsView.as_view(), name='reports_server_hosts'),
    url(r'^$', views.DashboardView.as_view(), name='reports_dashboard'),
]
