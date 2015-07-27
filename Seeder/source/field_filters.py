import models
import django_filters

from core.utils import EmptyFilter


class SourceFilter(EmptyFilter):
    publisher = django_filters.CharFilter(lookup_type='name__icontains')
    seed__url = django_filters.CharFilter(lookup_type='icontains')

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'seed__url', 'publisher', 'state',
                  'category', 'sub_category', 'suggested_by', 'created',
                  'last_changed')
