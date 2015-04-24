import models as core_models
import django_filters

from django.db import models
from django_filters.filters import ChoiceFilter

EMPTY_CHOICE = ('', '---------')


class SourceFilter(django_filters.FilterSet):
    filter_overrides = {
        models.CharField: {
            'filter_class': django_filters.CharFilter,
            'extra': lambda f: {
                'lookup_type': 'icontains',
            }
        }
    }
    
    def __init__(self, *args, **kwargs):
        # pylint: disable=E1002
        super(SourceFilter, self).__init__(*args, **kwargs)
        # add empty choice to all choice fields:
        choices = filter(
            lambda f: isinstance(self.filters[f], ChoiceFilter),
            self.filters)

        for field_name in choices:
            extended_choices = ((EMPTY_CHOICE,) +
                                self.filters[field_name].extra['choices'])
            self.filters[field_name].extra['choices'] = extended_choices

    class Meta:
        model = core_models.Source
        fields = ('name', 'owner', 'web_proposal', 'publisher', 'state',
                  'conspectus', 'sub_conspectus', 'created',  'last_changed')