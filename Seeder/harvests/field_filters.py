from . import models

from core.custom_filters import EmptyFilter


class HarvestFilter(EmptyFilter):
    class Meta:
        model = models.Harvest
        fields = ('harvest_type', 'target_frequency')
