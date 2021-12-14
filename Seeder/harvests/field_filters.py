from . import models
from core.custom_filters import BaseFilterSet


class TopicCollectionFilter(BaseFilterSet):
    class Meta:
        model = models.TopicCollection
        fields = {
            'title': ('icontains',),
        }


class ExternalTopicCollectionFilter(BaseFilterSet):
    class Meta:
        model = models.ExternalTopicCollection
        fields = {
            'title': ('icontains',),
        }


class HarvestConfigFilter(BaseFilterSet):
    class Meta:
        model = models.HarvestConfiguration
        fields = (
            'harvest_type', 'duration', 'budget', 'dataLimit', 'documentLimit',
            'deduplication',
        )
