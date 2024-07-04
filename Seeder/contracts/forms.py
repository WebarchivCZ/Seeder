from . import models
from contracts.constants import CREATIVE_COMMONS_TYPES_CHOICES

from dal import autocomplete
from django import forms


class ContractForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('state', 'year', 'contract_number', 'valid_from', 'valid_to',
                  'contract_file', 'creative_commons_type',
                  'parent_contract', 'description',
                  'in_communication')
        widgets = {
            'creative_commons_type': forms.Select(
                choices=CREATIVE_COMMONS_TYPES_CHOICES),
            'description': forms.Textarea(attrs={"rows": 2}),
            'parent_contract': autocomplete.ModelSelect2(
                url='contracts:autocomplete',
            ),
        }


class AssignForm(forms.Form):
    contract = forms.ModelChoiceField(models.Contract.objects.none())


class EmailForm(forms.ModelForm):
    class Meta:
        model = models.EmailNegotiation
        fields = ('scheduled_date', 'title', 'content')
