from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.urls.base import reverse_lazy
from django.views.generic import RedirectView

from rest_framework.authtoken import views as token_views
from urljects import U, url, view_include

from core import views as core_views
from source import views as source_views
from publishers import views as publisher_views
from voting import views as voting_views
from contracts import views as contracts_views
from harvests import views as harvests_views
from blacklists import views as blacklists_views
from search_blob import views as search_views

from qa import views as qa_views
from www import views as www_views
from www import views_non_localized
from www import news_admin_views

from api import api_router


admin.site.index_title = admin.site.site_header = admin.site.site_title = 'Administrace WWW'



auth_urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^password_change/$', auth_views.password_change, name='password_change'),
    url(r'^password_change/done/$', core_views.PasswordChangeDone.as_view(), name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', core_views.PasswordChangeDone.as_view(), name='password_reset_complete'),
]

seeder_urlpatterns = [
    url(U / 'ckeditor', include('ckeditor_uploader.urls')),
    url(U / 'api' / 'auth', include(
        'rest_framework.urls', namespace='rest_framework')),
    url(U / 'api' / 'token', token_views.obtain_auth_token),
    url(U / 'search', view_include(search_views, namespace='search')),

    url(U / 'api', include(api_router.urls)),
    url(U / 'source', view_include(source_views, namespace='source')),
    url(U / 'publisher', view_include(publisher_views, namespace='publishers')),    # noqa
    url(U / 'voting', view_include(voting_views, namespace='voting')),
    url(U / 'contracts', view_include(contracts_views, namespace='contracts')),
    url(U / 'harvests', view_include(harvests_views, namespace='harvests')),
    url(U / 'blacklists', view_include(blacklists_views, namespace='blacklists')),  # noqa
    url(U / 'qa', view_include(qa_views, namespace='qa')),

    url(U / 'news', view_include(news_admin_views, namespace='news')),

    # beware: wild card regexp!
    url(U, view_include(core_views, namespace='core'))
]

disclaimer_redirect = RedirectView.as_view(
    url=reverse_lazy('www:disclaimer'),
    permanent=True
)

urlpatterns = [
    # Legacy redirects:
    url(r'^certifikat/$', RedirectView.as_view(url=reverse_lazy('www:about_graphics'), permanent=True)),
    url(r'^cs/certifikovano/$', disclaimer_redirect),
    url(r'^en/disclaimer/$', disclaimer_redirect),
    url(r'^files/vydavatele/certifikat.html$', disclaimer_redirect),

    url(U / 'admin', include(admin.site.urls)),
    url(U / 'auth', include(auth_urlpatterns)),
    url(U / 'seeder', include(seeder_urlpatterns)),
    url(U / 'lang', view_include(views_non_localized, namespace='www_no_lang')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url(U, view_include(www_views, namespace='www')),
)