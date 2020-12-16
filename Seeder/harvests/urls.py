from datetime import date
from django.utils import dateparse
from django.urls import path, re_path, register_converter
from .views import *

# TODO move to 'core' if used anywhere else


class DateConverter:
    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        return dateparse.parse_date(value)

    def to_url(self, value):
        if type(value) == date:
            return "{:%Y-%m-%d}".format(value)
        else:
            return str(value)


register_converter(DateConverter, 'date')

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'),
    path('json', CalendarJsonView.as_view(), name='json_calendar'),
    path('add', AddView.as_view(), name='add'),
    path('<int:pk>/detail', Detail.as_view(), name='detail'),
    path('<int:pk>/edit', Edit.as_view(), name='edit'),
    path('add_topic_collection', AddTopicCollection.as_view(),
         name='topic_collection_add'),
    path('<int:pk>/change_order/<str:to>', ChangeOrder.as_view(),
         name='topic_collection_change_order'),
    path('<int:pk>/collection_edit', EditCollection.as_view(),
         name='topic_collection_edit'),
    path('<int:pk>/collection_detail', CollectionDetail.as_view(),
         name='topic_collection_detail'),
    path('<int:pk>/collection_history', CollectionHistory.as_view(),
         name='topic_collection_history'),
    path('<int:pk>/toggle_publish', CollectionTogglePublish.as_view(),
         name='topic_collection_toggle_publish'),
    path('<int:pk>/update_slug', CollectionUpdateSlug.as_view(),
         name='topic_collection_update_slug'),
    path('collections', CollectionListView.as_view(),
         name='topic_collection_list'),
    path('collections/reorder', ReorderCollections.as_view(),
         name='topic_collection_reorder'),
    # Harvest URLs
    path('catalogue', HarvestUrlCatalogue.as_view(), name='catalogue'),
    # Harvest URLs based on date and harvest id
    path('<date:h_date>/harvests', ListHarvestUrls.as_view(),
         name='harvest_urls'),
    path('<int:pk>/urls', ListUrls.as_view(), name='urls'),
    # Harvest URLs based on type
    path('<date:h_date>/shortcut_urls',
         ListShortcutUrlsByDate.as_view(), name='shortcut_urls_by_date'),
    path('<date:h_date>/seeds-<date:h_date2>-<str:shortcut>.txt',
         ListUrlsByDateAndShortcut.as_view(),
         name='shortcut_urls_by_date_and_type'),
]
