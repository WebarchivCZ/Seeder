import models

from django import forms


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('date_start', 'date_end', 'contract_type')


class EditForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('state', 'date_start', 'date_end', 'contract_file',
                  'contract_type', 'in_communication')
