from django import forms
from dal import autocomplete
from .models import Harvest


autocomplete_widgets = {
    'custom_sources': autocomplete.ModelSelect2Multiple(
        url='source:source_autocomplete'
    )
}


class HarvestCreateForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = [
            'scheduled_on',
            'title',
            'target_frequency',
            'custom_seeds',
            'custom_sources'
        ]
        widgets = autocomplete_widgets


class HarvestEditForm(forms.ModelForm):

    class Meta:
        model = Harvest
        fields = [
            'active',
            'scheduled_on',
            'title',
            'target_frequency',
            'custom_seeds',
            'custom_sources',
        ]

        widgets = autocomplete_widgets
