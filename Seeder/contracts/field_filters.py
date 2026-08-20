from . import models
from django.db.models import Q
import django_filters

from core.custom_filters import BaseFilterSet, DateRangeFilter


def filter_contract_number(queryset, name, value):
    # Use the ContractQuerySet method for consistent filtering logic
    return queryset.filter_by_contract_number(value)


def filter_creative_commons(queryset, name, value):
    ''' Filter whether a CC type is set or not '''
    query = Q(creative_commons_type=None) | Q(creative_commons_type='')
    if value:
        return queryset.exclude(query)
    else:
        return queryset.filter(query)


class ContractFilter(BaseFilterSet):
    valid_from = DateRangeFilter()
    valid_to = DateRangeFilter()

    contract_number = django_filters.CharFilter(
        field_name='contract_number', method=filter_contract_number)
    is_cc = django_filters.BooleanFilter(field_name='is_cc', label='CC')

    class Meta:
        model = models.Contract
        fields = {
            'contract_number': ('exact',),
            'publisher__name': ('icontains',),
            'state': ('exact',),
            'valid_from': ('exact',),
            'valid_to': ('exact',),
            'in_communication': ('exact',),
        }
