from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    # url(r'^password_change/$', auth_views.password_change, name='password_change'),
    # url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    # url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),
    # url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),


    url(r'^source/', include('source.urls')),
    url(r'^publisher/', include('publishers.urls')),
    url(r'^voting/', include('voting.urls')),

    # beware: wild card regexp!
    url(r'^', include('core.urls'))
)
