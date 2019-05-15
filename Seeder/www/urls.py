from django.urls import path, re_path, include
from django.utils.translation import ugettext_lazy as _
from . import news_admin_views as naw
from . import views_non_localized as vnl
from . import views as www

urlpatterns_news_admin = [
    path('add', naw.AddNews.as_view(), name='add'),
    path('<int:pk>/publish', naw.Publish.as_view(), name='publish'),
    path('<int:pk>/detail', naw.Detail.as_view(), name='detail'),
    path('<int:pk>/edit', naw.Edit.as_view(), name='edit'),
    path('<int:pk>/history', naw.History.as_view(), name='history'),
    path('', naw.ListView.as_view(), name='list'),
]

urlpatterns_non_localized = [
    path('lang/<str:code>', vnl.ChangeLanguage.as_view(), name='change_language'),
]

urlpatterns_www = [
    re_path(r'^$', www.Index.as_view(), name='index'),
    re_path(_('^topic_collections_url$'), www.TopicCollections.as_view(),
            name='topic_collections'),
    re_path(_('^topic_collections_url/(?P<slug>[\w-]+)$'),
            www.CollectionDetail.as_view(),
            name='collection_detail'),

    re_path(_('^about_url$'), www.About.as_view(), name='about'),
    re_path(_('^more_about_url$'), www.MoreAbout.as_view(), name='more_about'),
    re_path(_('^about_harvests_url$'),
            www.AboutHarvest.as_view(), name='about_harvests'),
    re_path(_('^about_terminology_url$'),
            www.AboutTerminology.as_view(), name='about_terminology'),
    re_path(_('^about_documents_url$'),
            www.AboutDocuments.as_view(), name='about_documents'),
    re_path(_('^about_graphics_url$'),
            www.AboutGraphics.as_view(), name='about_graphics'),
    re_path(_('^about_contact_url$'),
            www.AboutContact.as_view(), name='about_contact'),
    re_path(_('^about_faq_url$'), www.AboutFAQ.as_view(), name='about_faq'),

    re_path(_('^categories_url$'), www.Categories.as_view(), name='categories'),
    re_path(_('^categories_url/(?P<slug>[\w-]+)$'),
            www.CategoryDetail.as_view(),
            name='category_detail'),
    re_path(_('^categories_url/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)$'),
            www.SubCategoryDetail.as_view(),
            name='sub_category_detail'),

    re_path(_('^change_list_view/(?P<list_type>visual|text)$'),
            www.ChangeListView.as_view(),
            name='change_list_view'),

    re_path(_('^keyword_url/(?P<slug>[\w-]+)$'),
            www.KeywordViews.as_view(),
            name='keyword'),

    re_path(_('^search_url$'), www.SearchRedirectView.as_view(),
            name='search_redirect'),
    re_path(_('^search_url/(?P<query>.*)'), www.SearchView.as_view(),
            name='search'),

    re_path(_('^www_source_url/(?P<slug>[\w-]+)$'),
            www.SourceDetail.as_view(),
            name='source_detail'),

    re_path(_('^www_nominate_url$'), www.Nominate.as_view(), name='nominate'),
    re_path(_('^www_nominate_success_url$'), www.NominateSuccess.as_view(),
            name='nominate_success'),
    re_path(_('^www_nominate_url/contract_url$'),
            www.NominateContractView.as_view(),
            name='nominate_contract'),
    re_path(_('^www_nominate_url/cooperation_url$'),
            www.NominateCooperationView.as_view(),
            name='nominate_cooperation'),
    re_path(_('^www_nominate_url/creative_commons_url$'),
            www.NominateCreativeCommonsView.as_view(),
            name='nominate_creative_commons'),
    re_path(_('^www_nominate_url/error_url$'),
            www.NominateErrorView.as_view(),
            name='nominate_error'),
    re_path(_('^www_nominate_url/feedback_url$'),
            www.NominateFeedbackView.as_view(),
            name='nominate_feedback'),
    re_path(_('^www_nominate_url/source_selection_url$'),
            www.NominateSourceSelectionView.as_view(),
            name='nominate_source_selection'),

    re_path(_('^disclaimer_url$'),
            www.DisclaimerView.as_view(),
            name='disclaimer'),

    re_path(_('^embed_url$'),
            www.EmbedView.as_view(),
            name='embed'),
]

urlpatterns = [
    path('seeder/news/', include((urlpatterns_news_admin, 'www'), namespace='news')),
    path('lang/', include((urlpatterns_non_localized, 'www'), namespace='www_no_lang')),
]
