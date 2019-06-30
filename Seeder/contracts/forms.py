from . import models
from contracts.constants import CREATIVE_COMMONS_TYPES_CHOICES

from django import forms


class ContractForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('state', 'year', 'contract_number', 'valid_from', 'valid_to',
                  'contract_file', 'creative_commons', 'creative_commons_type',
                  'in_communication')
        widgets = {
            'creative_commons_type': forms.Select(
                choices=CREATIVE_COMMONS_TYPES_CHOICES)
        }


class AssignForm(forms.Form):
    contract = forms.ModelChoiceField(models.Contract.objects.none())


class EmailForm(forms.ModelForm):
    class Meta:
        model = models.EmailNegotiation
        fields = ('scheduled_date', 'title', 'content')
