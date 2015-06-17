import autocomplete_light

from django.utils.translation import ugettext_lazy as _
from models import SubCategory


class AutocompleteSubCategory(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name', 'subcategory_id']
    attrs = {
        'placeholder': _('Sub category'),
        'data-autocomplete-minimum-characters': 1,
    }
    widget_attrs = {
        # 'class': 'modern-style',
    }

autocomplete_light.register(SubCategory, AutocompleteSubCategory)
