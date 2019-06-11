from . import models

from core.custom_filters import BaseFilterSet


class NewsFilter(BaseFilterSet):
    class Meta:
        model = models.NewsObject
        fields = {
            'title': ('icontains',),
        }
