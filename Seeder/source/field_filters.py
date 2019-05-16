import django_filters

from dal import autocomplete
from core.custom_filters import BaseFilterSet, DateRangeFilter
from publishers.models import Publisher
from .import models


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
        }
