from django.conf.urls import patterns, url, include

urlpatterns = patterns('openipam.dns.views',

    url(r'^$', 'index', name='dns'),
)




