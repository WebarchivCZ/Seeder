from datetime import date
from django.utils import dateparse
from django.urls import path, register_converter, include
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

# Internal Topic Collections
internal_collections_urlpatterns = [
    path('', InternalCollectionListView.as_view(),
         name='internal_collection_list'),
    path('add', InternalCollectionAdd.as_view(),
         name='internal_collection_add'),
    path('<int:pk>/edit', InternalCollectionEdit.as_view(),
         name='internal_collection_edit'),
    path('<int:pk>', InternalCollectionDetail.as_view(),
         name='internal_collection_detail'),
    path('<int:pk>/urls', InternalCollectionListUrls.as_view(),
         name='internal_collection_urls'),
    path('<int:pk>/history', InternalCollectionHistory.as_view(),
         name='internal_collection_history'),
]

# External Topic Collections
external_collections_urlpatterns = [
    path('', ExternalCollectionListView.as_view(),
         name='external_collection_list'),
    path('add', ExternalCollectionAdd.as_view(),
         name='external_collection_add'),
    path('<int:pk>/edit', ExternalCollectionEdit.as_view(),
         name='external_collection_edit'),
    path('<int:pk>', ExternalCollectionDetail.as_view(),
         name='external_collection_detail'),
    path('<int:pk>/urls', ExternalCollectionListUrls.as_view(),
         name='external_collection_urls'),
    path('<int:pk>/history', ExternalCollectionHistory.as_view(),
         name='external_collection_history'),
    # Ordering, slug, publishing
    path('<int:pk>/toggle_publish',
         ExternalCollectionTogglePublish.as_view(),
         name='external_collection_toggle_publish'),
    path('<int:pk>/update_slug',
         ExternalCollectionUpdateSlug.as_view(),
         name='external_collection_update_slug'),
    path('<int:pk>/change_order/<str:to>',
         ExternalCollectionChangeOrder.as_view(),
         name='external_collection_change_order'),
    path('collections/reorder',
         ExternalCollectionsReorder.as_view(),
         name='external_collections_reorder'),
]


urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'),
    path('json', CalendarJsonView.as_view(), name='json_calendar'),
    path('add', AddView.as_view(), name='add'),
    path('<int:pk>/detail', Detail.as_view(), name='detail'),
    path('<int:pk>/edit', Edit.as_view(), name='edit'),
    # Topic Collections (Internal & External)
    path('collections/internal/', include(internal_collections_urlpatterns)),
    path('collections/external/', include(external_collections_urlpatterns)),
    # Harvest URLs
    path('catalogue', HarvestUrlCatalogue.as_view(), name='catalogue'),
    # Harvest URLs based on date and harvest id
    path('<date:h_date>/harvests', ListHarvestUrls.as_view(),
         name='harvest_urls'),
    path('<int:pk>/urls', ListUrls.as_view(), name='urls'),
    path('<int:pk>/json', JsonUrls.as_view(), name='json'),
    # Harvest URLs based on type
    path('<date:h_date>/shortcut_urls',
         ListShortcutUrlsByDate.as_view(), name='shortcut_urls_by_date'),
    path('<date:h_date>/seeds-<date:h_date2>-<str:shortcut>.txt',
         ListUrlsByDateAndShortcut.as_view(),
         name='shortcut_urls_by_date_and_type'),
]
