import django_filters

from django.utils.translation import ugettext_lazy as _
from dal import autocomplete
from core.custom_filters import BaseFilterSet, DateRangeFilter
from publishers.models import Publisher
from .import models


def filter_not_empty(queryset, name, value):
    lookup_isnull = '__'.join([name, 'isnull'])
    lookup_empty = '__'.join([name, 'exact'])
    q = queryset.filter(**{lookup_isnull: not value})
    if value:
        return q.exclude(**{lookup_empty: ''})
    else:
        empty = queryset.filter(
            aleph_id__exact='').values_list('pk', flat=True)
        null = q.values_list('pk', flat=True)
        return queryset.filter(pk__in=list(empty) + list(null))


class SourceFilter(BaseFilterSet):
    publisher = django_filters.ModelChoiceFilter(
        queryset=Publisher.objects.all(),
        widget=autocomplete.ModelSelect2(url='publishers:autocomplete')
    )

    category = django_filters.ModelChoiceFilter(
        queryset=models.Category.objects.all(),
        widget=autocomplete.ModelSelect2(url='source:category_autocomplete')
    )

    sub_category = django_filters.ModelChoiceFilter(
        queryset=models.SubCategory.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='source:subcategory_autocomplete',
            forward=['category']
        )
    )

    has_alephid = django_filters.BooleanFilter(label=_('Source is catalogized'),
                                               field_name='aleph_id',
                                               method=filter_not_empty)
    has_issn = django_filters.BooleanFilter(label=_('Source is periodic'),
                                            field_name='issn',
                                            method=filter_not_empty)

    created = DateRangeFilter()
    last_changed = DateRangeFilter()

    class Meta:
        model = models.Source
        fields = {
            'name': ('icontains',),
            'owner': ('exact',),
            'state': ('exact',),
            'publisher': ('exact',),
            'category': ('exact',),
            'sub_category': ('exact',),
            'suggested_by': ('exact',),
            'dead_source': ('exact',),
            'created': ('exact',),
            'last_changed': ('exact',),
            'has_alephid': ('exact',),
            'has_issn': ('exact',),
        }
