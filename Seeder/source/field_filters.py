import models
import django_filters

from core.utils import EmptyFilter


class SourceFilter(EmptyFilter):
    publisher = django_filters.CharFilter(lookup_type='name__icontains')

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'publisher', 'state',
                  'category', 'sub_category', 'suggested_by', 'created',
                  'last_changed')
