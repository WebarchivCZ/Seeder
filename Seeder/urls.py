from django.conf.urls import patterns, include, url
from django.contrib import admin

auth_patterns = patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
    url(r'^passwd/$', 'password_change', name='passwd'),
    url(r'^passwd/done/$', 'password_change_done', name='passwd_done'),
    url(r'^reset/$', 'password_reset', name='passwd_reset'),
    url(r'^reset/done/$', 'password_reset_done', name='passwd_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm', name='reset_confirm'),  # noqa
    url(r'^reset/done/$', 'password_reset_complete', name='reset_complete'),
)

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include(auth_patterns, namespace='auth')),
    url(r'^source/', include('source.urls', namespace='source')),
    url(r'^publisher/', include('publishers.urls', namespace='publishers')),
    url(r'^voting/', include('voting.urls', namespace='voting')),

    # beware: wild card regexp!
    url(r'^', include('core.urls', namespace='core'))
)
