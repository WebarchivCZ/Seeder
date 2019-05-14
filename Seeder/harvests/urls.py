from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'),
    path('json', CalendarJsonView.as_view(), name='json_calendar'),
    path('add', AddView.as_view(), name='add'),
    path('<int:pk>/detail', Detail.as_view(), name='detail'),
    path('<int:pk>/edit', Edit.as_view(), name='edit'),
    path('<int:pk>/urls', ListUrls.as_view(), name='urls'),
    re_path('(?P<h_date>\d{4}-\d{2}-\d{2})/(?P<h_type>\w+)/urls',
            ListUrlsByTimeAndType.as_view(), name='urls_by_time'),
    path('catalogue', HarvestUrlCatalogue.as_view(), name='catalogue'),
    path('add_topic_collection', AddTopicCollection.as_view(),
         name='topic_collection_add'),
    path('<int:pk>/collection_edit', EditCollection.as_view(),
         name='topic_collection_edit'),
    path('<int:pk>/collection_detail', CollectionDetail.as_view(),
         name='topic_collection_detail'),
    path('<int:pk>/collection_history', CollectionHistory.as_view(),
         name='topic_collection_history'),
    path('collections', CollectionListView.as_view(),
         name='topic_collection_list'),
]
