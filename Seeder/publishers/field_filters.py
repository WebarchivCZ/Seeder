from . import models

from core.custom_filters import BaseFilterSet


class PublisherFilter(BaseFilterSet):
    class Meta:
        model = models.Publisher
        fields = {
            'name': ('iexact', 'icontains'),
        }
