from django import forms
from .models import Harvest


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        exclude = [
            'custom_sources',
            'custom_seeds',
            'harvest_type',
            'active'
        ]
