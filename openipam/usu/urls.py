from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView


urlpatterns = patterns('openipam.usu.views',

    url(r'^overview/$', 'overview', name='overview'),
    url(r'^leases/usage/$', 'lease_usage', name='lease_usage'),
    url(r'^leases/available/$', 'leases_available', name='leases_available'),
    url(r'^weathermap/$', 'weather_map', name='weather_map'),
    #url(r'^add/$', 'add', name='add_hosts'),
)
