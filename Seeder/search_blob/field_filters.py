from www.models import SearchLog
from core.custom_filters import BaseFilterSet


class SearchLogFilter(BaseFilterSet):
    class Meta:
        model = SearchLog
        fields = {
            'search_term': ('exact', 'icontains'),
            'ip_address': ('icontains',),
        }
