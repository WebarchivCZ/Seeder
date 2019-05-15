from django.urls import path, re_path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls.base import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns

from rest_framework.authtoken import views as token_views
from api import api_router
from www.urls import urlpatterns_www

admin.site.index_title = admin.site.site_header = admin.site.site_title = 'Administrace WWW'  # noqa

seeder_urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/auth/', include(
        ('rest_framework.urls', 'rest_framework'), namespace='rest_framework')),
    path('api/token/', token_views.obtain_auth_token),
    path('search/', include(('search_blob.urls', 'search_blob'), namespace='search')),

    path('api/', include(api_router.urls)),
    path('source/', include(('source.urls', 'source'), namespace='source')),
    path('publisher/', include(('publishers.urls', 'publishers'), namespace='publishers')),    # noqa
    path('voting/', include(('voting.urls', 'voting'), namespace='voting')),
    path('contracts/', include(('contracts.urls', 'contracts'), namespace='contracts')),
    path('harvests/', include(('harvests.urls', 'harvests'), namespace='harvests')),
    path('blacklists/', include(('blacklists.urls', 'blacklists'), namespace='blacklists')),  # noqa
    path('qa/', include(('qa.urls', 'qa'), namespace='qa')),

    path('', include(('core.urls', 'core'), namespace='core'))
]

disclaimer_redirect = RedirectView.as_view(
    url=reverse_lazy('www:disclaimer'),
    permanent=True
)

urlpatterns = [
    # Legacy redirects:
    path('certifikat', RedirectView.as_view(
        url=reverse_lazy('www:about_graphics'), permanent=True)
    ),
    path('cs/certifikovano/', disclaimer_redirect),
    path('en/disclaimer/', disclaimer_redirect),
    path('files/vydavatele/certifikat.html', disclaimer_redirect),

    path('seeder/admin/', admin.site.urls),
    path('seeder/auth/', include('django.contrib.auth.urls')),
    path('seeder/', include(seeder_urlpatterns)),
    path('', include('www.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include((urlpatterns_www, 'www'), namespace='www')),
)
