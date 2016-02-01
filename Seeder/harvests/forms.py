from django import forms
from .models import Harvest


class HarvestCreateForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = [
            'scheduled_on',
            'target_frequency',
            'custom_seeds',
        ]
