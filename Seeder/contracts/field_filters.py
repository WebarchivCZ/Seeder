from . import models

from core.custom_filters import BaseFilterSet, DateRangeFilter


class ContractFilter(BaseFilterSet):
    valid_from = DateRangeFilter()
    valid_to = DateRangeFilter()

    class Meta:
        model = models.Contract
        fields = {
            'publisher__name': ('icontains',),
            'state': ('exact',),
            'valid_from': ('exact',),
            'valid_to': ('exact',),
            'creative_commons': ('exact',),
            'in_communication': ('exact',),
        }
