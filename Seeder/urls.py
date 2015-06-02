from django.conf.urls import patterns, include, url
from django.contrib import admin

from core.views import PasswordChangeDone

auth_patterns = patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
    url(r'^passwd/$', 'password_change', name='password_change'),
    url(r'^reset/$', 'password_reset', name='password_reset'),
    url(r'^reset/done/$', 'password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm', name='password_reset_confirm'),  # noqa
    url(r'^reset/complete/$', PasswordChangeDone.as_view(), name='password_reset_complete'),  # noqa
    url(r'^passwd/done/$', PasswordChangeDone.as_view(), name='password_change_done'),  # noqa

)

urlpatterns = patterns(
    '',
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include(auth_patterns)),
    url(r'^source/', include('source.urls', namespace='source')),
    url(r'^publisher/', include('publishers.urls', namespace='publishers')),
    url(r'^voting/', include('voting.urls', namespace='voting')),
    url(r'^contracts/', include('contracts.urls', namespace='contracts')),

    # beware: wild card regexp!
    url(r'^', include('core.urls', namespace='core'))
)
