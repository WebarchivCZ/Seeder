import models
import django_filters

from core.custom_filters import EmptyFilter, DateRangeFilter
from core.widgets import DateRangeWidget


class SourceFilter(EmptyFilter):
    publisher = django_filters.CharFilter(lookup_type='name__icontains')
    seed__url = django_filters.CharFilter(lookup_type='icontains')

    created = DateRangeFilter()

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'seed__url', 'publisher', 'state',
                  'category', 'sub_category', 'suggested_by', 'created',
                  'last_changed')
