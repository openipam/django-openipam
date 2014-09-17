from django.conf.urls import patterns, url, include


urlpatterns = patterns('openipam.usu.views',

    url(r'^overview/$', 'overview', name='overview'),
    url(r'^leases/$', 'available_leases', name='available_leases'),
    url(r'^weathermap/$', 'weather_map', name='weather_map'),
    #url(r'^add/$', 'add', name='add_hosts'),
)
