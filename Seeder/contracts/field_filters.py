from . import models

from core.custom_filters import EmptyFilter, DateRangeFilter


class ContractFilter(EmptyFilter):
    valid_to = DateRangeFilter()
    valid_from = DateRangeFilter()

    class Meta:
        model = models.Contract
        fields = ('state', 'valid_from', 'valid_to', 'creative_commons',
                  'in_communication')
