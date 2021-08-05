from . import models
from core.custom_filters import BaseFilterSet


class TopicCollectionFilter(BaseFilterSet):
    class Meta:
        model = models.TopicCollection
        fields = {
            'status': ('exact',),
            'title': ('icontains',),
        }


class ExternalTopicCollectionFilter(BaseFilterSet):
    class Meta:
        model = models.ExternalTopicCollection
        fields = {
            'title': ('icontains',),
        }
