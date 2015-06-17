import autocomplete_light

from models import Publisher


autocomplete_light.register(
    Publisher,
    search_fields=['^name'],
    attrs={
        'placeholder': 'Publisher',
        'data-autocomplete-minimum-characters': 1,
    },
    widget_attrs={
        'data-widget-maximum-values': 5,
        # 'class': 'modern-style',
    }
)
