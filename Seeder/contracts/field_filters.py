from . import models
from django.db.models import Q
import django_filters

from core.custom_filters import BaseFilterSet, DateRangeFilter


def filter_contract_number(queryset, name, value):
    # value in format e.g. '64 / 2017'
    try:
        contract_number, year = [int(s.strip()) for s in value.split('/')]
        return queryset.filter(contract_number=contract_number, year=year)
    except Exception:
        return queryset.none()


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
    creative_commons = django_filters.BooleanFilter(
        method=filter_creative_commons)

    class Meta:
        model = models.Contract
        fields = {
            'contract_number': ('exact',),
            'publisher__name': ('icontains',),
            'state': ('exact',),
            'valid_from': ('exact',),
            'valid_to': ('exact',),
            'creative_commons': ('exact',),
            'in_communication': ('exact',),
        }
