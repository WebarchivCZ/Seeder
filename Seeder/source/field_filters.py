import django_filters

from dal import autocomplete
from core.custom_filters import EmptyFilter, DateRangeFilter
from publishers.models import Publisher
from .import models


class SourceFilter(EmptyFilter):
    seed__url = django_filters.CharFilter(lookup_expr='icontains')

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
        fields = ('name', 'owner', 'seed__url', 'publisher', 'state',
                  'category', 'sub_category', 'suggested_by', 'created',
                  'last_changed', 'dead_source',)
