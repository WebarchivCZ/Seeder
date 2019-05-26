from django.urls import path, re_path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls.base import reverse_lazy
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns

from www import news_admin_views as naw
from www import views_non_localized as vnl

from rest_framework.authtoken import views as token_views
from api import api_router

admin.site.index_title = admin.site.site_header = admin.site.site_title = 'Administrace WWW'  # noqa

urlpatterns_news_admin = [
    path('add', naw.AddNews.as_view(), name='add'),
    path('<int:pk>/publish', naw.Publish.as_view(), name='publish'),
    path('<int:pk>/detail', naw.Detail.as_view(), name='detail'),
    path('<int:pk>/edit', naw.Edit.as_view(), name='edit'),
    path('<int:pk>/history', naw.History.as_view(), name='history'),
    path('', naw.ListView.as_view(), name='list'),
]

seeder_urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/auth/', include(('rest_framework.urls', 'rest_framework'),
        namespace='rest_framework')),
    path('api/token/', token_views.obtain_auth_token),
    path('search/', include(('search_blob.urls', 'search_blob'),
        namespace='search')),

    path('api/', include(api_router.urls)),
    path('source/', include(('source.urls', 'source'), namespace='source')),
    path('publisher/', include(('publishers.urls', 'publishers'),
        namespace='publishers')),    # noqa
    path('voting/', include(('voting.urls', 'voting'), namespace='voting')),
    path('contracts/', include(('contracts.urls', 'contracts'),
        namespace='contracts')),
    path('harvests/', include(('harvests.urls', 'harvests'),
        namespace='harvests')),
    path('blacklists/', include(('blacklists.urls', 'blacklists'),
        namespace='blacklists')),  # noqa
    path('qa/', include(('qa.urls', 'qa'), namespace='qa')),
    path('news/', include((urlpatterns_news_admin, 'www'), namespace='news')),

    path('', include(('core.urls', 'core'), namespace='core'))
]

disclaimer_redirect = RedirectView.as_view(
    url=reverse_lazy('www:disclaimer'),
    permanent=True
)

urlpatterns_non_localized = [
    path('<str:code>', vnl.ChangeLanguage.as_view(),
         name='change_language'),
]

urlpatterns = [
    # Legacy redirects:
    path('certifikat', RedirectView.as_view(
        url=reverse_lazy('www:about_graphics'), permanent=True),
        name='certifikat'),
    path('cs/certifikovano/', disclaimer_redirect, name='disclaimer_cs'),
    path('en/disclaimer/', disclaimer_redirect, name='disclaimer_en'),
    path('files/vydavatele/certifikat.html', disclaimer_redirect,
         name='disclaimer_file'),

    path('seeder/admin/', admin.site.urls),
    path('seeder/auth/', include('django.contrib.auth.urls')),
    path('seeder/', include(seeder_urlpatterns)),
    path('lang/', include((urlpatterns_non_localized, 'www'),
                          namespace='www_no_lang')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include(('www.urls', 'www'), namespace='www')),
)
