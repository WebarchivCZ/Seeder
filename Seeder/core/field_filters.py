import models

from django_filters import FilterSet


class SourceFilter(FilterSet):
    class Meta:
        model = models.Source
        fields = ('name', 'publisher')