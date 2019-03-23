import django_tables2 as tables

from www.models import SearchLog


class SearchLogTable(tables.Table):
    class Meta:
        model = SearchLog
        fields = (
            'search_term',
            'log_time',
            'ip_address',
        )
        attrs = {
            'class': 'table table-striped table-hover'
        }
        order_by = '-log_time'
