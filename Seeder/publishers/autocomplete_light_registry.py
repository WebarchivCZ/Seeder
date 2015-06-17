import autocomplete_light

from django.utils.translation import ugettext_lazy as _
from models import Publisher


class AutocompletePublisher(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name']
    attrs = {
        'placeholder': _('Publisher'),
        'data-autocomplete-minimum-characters': 1,
    }
    widget_attrs = {
        'data-widget-maximum-values': 5,
        # 'class': 'modern-style',
    }

autocomplete_light.register(Publisher, AutocompletePublisher)
