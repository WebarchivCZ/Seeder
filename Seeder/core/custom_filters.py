import django_filters

from django.db import models
from core.widgets import RangeField


class BaseFilterSet(django_filters.FilterSet):
    """
    Filter that filters based upon icontains lookup
    """
    class Meta:
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                }
            }
        }


class DateRangeFilter(django_filters.Filter):
    """
    Filter that has two fields and sets limits on the filter - it can be
    open range filter.
    """
    field_class = RangeField

    def filter(self, qs, value):
        # When no value is passed (filter not used), return default
        if value is None:
            return qs
        date_from, date_to = value
        filter_queries = {}
        if date_from:
            filter_queries['{0}__gte'.format(self.field_name)] = date_from
        if date_to:
            filter_queries['{0}__lte'.format(self.field_name)] = date_to

        if filter_queries:
            return qs.filter(**filter_queries)
        return qs
