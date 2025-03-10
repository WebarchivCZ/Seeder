from . import models
from core.custom_filters import BaseFilterSet, DateRangeFilter


class TopicCollectionFilter(BaseFilterSet):
    class Meta:
        model = models.TopicCollection
        fields = {
            "title": ("icontains",),
        }


class ExternalTopicCollectionFilter(BaseFilterSet):
    class Meta:
        model = models.ExternalTopicCollection
        fields = {
            "title": ("icontains",),
        }


class HarvestFilter(BaseFilterSet):
    scheduled_on = DateRangeFilter()

    class Meta:
        model = models.Harvest
        fields = {
            "title": ("icontains",),
            "status": ("exact",),
            "harvest_type": ("exact",),
            "annotation": ("icontains",),
            # "scheduled_on": DateRangeFilter()
        }


class HarvestConfigFilter(BaseFilterSet):
    class Meta:
        model = models.HarvestConfiguration
        fields = (
            "harvest_type", "duration", "budget", "dataLimit", "documentLimit",
            "deduplication",
        )
