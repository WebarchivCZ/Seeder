from django.urls import path
from .views import *

urlpatterns = [
    path('add', AddSource.as_view(), name='add'),
    path('detail/<int:pk>', SourceDetail.as_view(), name='detail'),
    path('edit/<int:pk>', SourceEdit.as_view(), name='edit'),
    path('<int:pk>/delete', DeleteView.as_view(), name='delete'),
    path('add_seed/<int:pk>', SeedAdd.as_view(), name='add_seed'),
    path('seed/<int:pk>', SeedEdit.as_view(), name='seed_edit'),
    path('history/<int:pk>', History.as_view(), name='history'),
    path('list', SourceList.as_view(), name='list'),
    path('export', SourceExportAll.as_view(), name='export'),
    path('category_autocomplete', CategoryAutocomplete.as_view(),
         name='category_autocomplete'),
    path('subcategory_autocomplete', SubcategoryAutocomplete.as_view(),
         name='subcategory_autocomplete'),
    path('source_autocomplete', SourceAutocomplete.as_view(),
         name='source_autocomplete'),
    path('source_public_autocomplete', SourcePublicAutocomplete.as_view(),
         name='source_public_autocomplete'),
    path('keyword_autocomplete', KeywordAutocomplete.as_view(),
         name='keyword_autocomplete'),
    path('dump', SourceDump.as_view(), name='dump'),
]
