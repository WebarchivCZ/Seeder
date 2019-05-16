from www.models import SearchLog
from core.custom_filters import EmptyFilter


class SearchLogFilter(EmptyFilter):
    class Meta:
        model = SearchLog
        fields = {
            'search_term': ('exact', 'icontains'),
            'ip_address': ('icontains',),
        }
