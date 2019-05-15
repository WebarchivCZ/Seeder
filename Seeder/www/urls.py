from django.urls import path, include
from . import news_admin_views as naw
from . import views_non_localized as vnl

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

urlpatterns = [
    path('seeder/news/', include((urlpatterns_news_admin, 'www'), namespace='news')),
    path('lang/', include((urlpatterns_non_localized, 'www'), namespace='www_no_lang')),
]
