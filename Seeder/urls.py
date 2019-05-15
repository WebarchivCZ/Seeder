from django.urls import path, re_path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls.base import reverse_lazy
from django.views.generic import RedirectView
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken import views as token_views
from api import api_router
from www import views as www_views


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

www_urls = [
    re_path(r'^$', www_views.Index.as_view(), name='index'),
    re_path(_('^topic_collections_url$'), www_views.TopicCollections.as_view(),
        name='topic_collections'),
    re_path(_('^topic_collections_url/(?P<slug>[\w-]+)$'),
        www_views.CollectionDetail.as_view(),
        name='collection_detail'),

    re_path(_('^about_url$'), www_views.About.as_view(), name='about'),
    re_path(_('^more_about_url$'), www_views.MoreAbout.as_view(), name='more_about'),
    re_path(_('^about_harvests_url$'), www_views.AboutHarvest.as_view(), name='about_harvests'),
    re_path(_('^about_terminology_url$'), www_views.AboutTerminology.as_view(), name='about_terminology'),
    re_path(_('^about_documents_url$'), www_views.AboutDocuments.as_view(), name='about_documents'),
    re_path(_('^about_graphics_url$'), www_views.AboutGraphics.as_view(), name='about_graphics'),
    re_path(_('^about_contact_url$'), www_views.AboutContact.as_view(), name='about_contact'),
    re_path(_('^about_faq_url$'), www_views.AboutFAQ.as_view(), name='about_faq'),

    re_path(_('^categories_url$'), www_views.Categories.as_view(), name='categories'),
    re_path(_('^categories_url/(?P<slug>[\w-]+)$'),
        www_views.CategoryDetail.as_view(),
        name='category_detail'),
    re_path(_('^categories_url/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)$'),
        www_views.SubCategoryDetail.as_view(),
        name='sub_category_detail'),

    re_path(_('^change_list_view/(?P<list_type>visual|text)$'),
        www_views.ChangeListView.as_view(),
        name='change_list_view'),

    re_path(_('^keyword_url/(?P<slug>[\w-]+)$'),
        www_views.KeywordViews.as_view(),
        name='keyword'),

    re_path(_('^search_url$'), www_views.SearchRedirectView.as_view(),
        name='search_redirect'),
    re_path(_('^search_url/(?P<query>.*)'), www_views.SearchView.as_view(),
        name='search'),

    re_path(_('^www_source_url/(?P<slug>[\w-]+)$'),
        www_views.SourceDetail.as_view(),
        name='source_detail'),

    re_path(_('^www_nominate_url$'), www_views.Nominate.as_view(), name='nominate'),
    re_path(_('^www_nominate_success_url$'), www_views.NominateSuccess.as_view(),
        name='nominate_success'),
    re_path(_('^www_nominate_url/contract_url$'),
        www_views.NominateContractView.as_view(),
        name='nominate_contract'),
    re_path(_('^www_nominate_url/cooperation_url$'),
        www_views.NominateCooperationView.as_view(),
        name='nominate_cooperation'),
    re_path(_('^www_nominate_url/creative_commons_url$'),
        www_views.NominateCreativeCommonsView.as_view(),
        name='nominate_creative_commons'),
    re_path(_('^www_nominate_url/error_url$'),
        www_views.NominateErrorView.as_view(),
        name='nominate_error'),
    re_path(_('^www_nominate_url/feedback_url$'),
        www_views.NominateFeedbackView.as_view(),
        name='nominate_feedback'),
    re_path(_('^www_nominate_url/source_selection_url$'),
        www_views.NominateSourceSelectionView.as_view(),
        name='nominate_source_selection'),

    re_path(_('^disclaimer_url$'),
        www_views.DisclaimerView.as_view(),
        name='disclaimer'),

    re_path(_('^embed_url$'),
        www_views.EmbedView.as_view(),
        name='embed'),
]


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
    # TODO: currently only loading news_admin and non_localized, the rest is solved below
    path('', include('www.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include((www_urls, 'www'), namespace='www')),
)