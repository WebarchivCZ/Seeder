from django.urls import path, re_path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls.base import reverse_lazy
from django.views.generic import RedirectView
from django.utils.translation import ugettext_lazy as _

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


admin.site.index_title = admin.site.site_header = admin.site.site_title = 'Administrace WWW'  # noqa

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
    url('', view_include(core_views, namespace='core'))
]

disclaimer_redirect = RedirectView.as_view(
    url=reverse_lazy('www:disclaimer'),
    permanent=True
)

www_urls = [
    url(r'^$', www_views.Index.as_view(), name='index'),
    url(_('^topic_collections_url$'), www_views.TopicCollections.as_view(),
        name='topic_collections'),
    url(_('^topic_collections_url/(?P<slug>[\w-]+)$'),
        www_views.CollectionDetail.as_view(),
        name='collection_detail'),

    url(_('^about_url$'), www_views.About.as_view(), name='about'),
    url(_('^more_about_url$'), www_views.MoreAbout.as_view(), name='more_about'),
    url(_('^about_harvests_url$'), www_views.AboutHarvest.as_view(), name='about_harvests'),
    url(_('^about_terminology_url$'), www_views.AboutTerminology.as_view(), name='about_terminology'),
    url(_('^about_documents_url$'), www_views.AboutDocuments.as_view(), name='about_documents'),
    url(_('^about_graphics_url$'), www_views.AboutGraphics.as_view(), name='about_graphics'),
    url(_('^about_contact_url$'), www_views.AboutContact.as_view(), name='about_contact'),
    url(_('^about_faq_url$'), www_views.AboutFAQ.as_view(), name='about_faq'),

    url(_('^categories_url$'), www_views.Categories.as_view(), name='categories'),
    url(_('^categories_url/(?P<slug>[\w-]+)$'),
        www_views.CategoryDetail.as_view(),
        name='category_detail'),
    url(_('^categories_url/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)$'),
        www_views.SubCategoryDetail.as_view(),
        name='sub_category_detail'),

    url(_('^change_list_view/(?P<list_type>visual|text)$'),
        www_views.ChangeListView.as_view(),
        name='change_list_view'),

    url(_('^keyword_url/(?P<slug>[\w-]+)$'),
        www_views.KeywordViews.as_view(),
        name='keyword'),

    url(_('^search_url$'), www_views.SearchRedirectView.as_view(),
        name='search_redirect'),
    url(_('^search_url/(?P<query>.*)'), www_views.SearchView.as_view(),
        name='search'),

    url(_('^www_source_url/(?P<slug>[\w-]+)$'),
        www_views.SourceDetail.as_view(),
        name='source_detail'),

    url(_('^www_nominate_url$'), www_views.Nominate.as_view(), name='nominate'),
    url(_('^www_nominate_success_url$'), www_views.NominateSuccess.as_view(),
        name='nominate_success'),
    url(_('^www_nominate_url/contract_url$'),
        www_views.NominateContractView.as_view(),
        name='nominate_contract'),
    url(_('^www_nominate_url/cooperation_url$'),
        www_views.NominateCooperationView.as_view(),
        name='nominate_cooperation'),
    url(_('^www_nominate_url/creative_commons_url$'),
        www_views.NominateCreativeCommonsView.as_view(),
        name='nominate_creative_commons'),
    url(_('^www_nominate_url/error_url$'),
        www_views.NominateErrorView.as_view(),
        name='nominate_error'),
    url(_('^www_nominate_url/feedback_url$'),
        www_views.NominateFeedbackView.as_view(),
        name='nominate_feedback'),
    url(_('^www_nominate_url/source_selection_url$'),
        www_views.NominateSourceSelectionView.as_view(),
        name='nominate_source_selection'),

    url(_('^disclaimer_url$'),
        www_views.DisclaimerView.as_view(),
        name='disclaimer'),

    url(_('^embed_url$'),
        www_views.EmbedView.as_view(),
        name='embed'),
]


urlpatterns = [
    # Legacy redirects:
    url(r'^certifikat/$', RedirectView.as_view(
        url=reverse_lazy('www:about_graphics'), permanent=True)
        ),
    url(r'^cs/certifikovano/$', disclaimer_redirect),
    url(r'^en/disclaimer/$', disclaimer_redirect),
    url(r'^files/vydavatele/certifikat.html$', disclaimer_redirect),

    url(U / 'seeder' / 'admin', include(admin.site.urls)),
    url(U / 'seeder' / 'auth', include('django.contrib.auth.urls')),
    url(U / 'seeder', include(seeder_urlpatterns)),
    url(U / 'lang', view_include(views_non_localized, namespace='www_no_lang')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url('^', include(www_urls, namespace='www')),
)