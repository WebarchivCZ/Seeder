from django.conf.urls import patterns, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken import views as token_views
from urljects import U, url, view_include

from core import views as core_views
from source import views as source_views
from publishers import views as publisher_views
from voting import views as voting_views
from contracts import views as contracts_views
from harvests import views as harvests_views

from api import api_router

auth_patterns = patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
    url(r'^passwd/$', 'password_change', name='password_change'),
    url(r'^reset/$', 'password_reset', name='password_reset'),
    url(r'^reset/done/$', 'password_reset_done', name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm', name='password_reset_confirm'),  # noqa
    url(r'^reset/complete/$', core_views.PasswordChangeDone.as_view(), name='password_reset_complete'),  # noqa
    url(r'^passwd/done/$', core_views.PasswordChangeDone.as_view(), name='password_change_done'),  # noqa
)

urlpatterns = patterns(
    '',
    url(U / 'ckeditor', include('ckeditor_uploader.urls')),
    url(U / 'admin', include(admin.site.urls)),
    url(U / 'auth', include(auth_patterns)),
    url(U / 'api' / 'auth', include(
        'rest_framework.urls', namespace='rest_framework')),
    url(U / 'autocomplete', include('autocomplete_light.urls')),
    url(U / 'api' / 'token', token_views.obtain_auth_token),

    url(U / 'api', include(api_router.urls)),
    url(U / 'source', view_include(source_views, namespace='source')),
    url(U / 'publisher', view_include(publisher_views, namespace='publishers')),  # noqa
    url(U / 'voting', view_include(voting_views, namespace='voting')),
    url(U / 'contracts', view_include(contracts_views, namespace='contracts')),
    url(U / 'harvests', view_include(harvests_views, namespace='harvests')),

    # beware: wild card regexp!
    url('^', view_include(core_views, namespace='core'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
