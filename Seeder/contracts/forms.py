import models

from django import forms


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('state', 'year', 'contract_number', 'valid_from', 'valid_to',
                  'contract_file', 'open_source', 'in_communication')


class AssignForm(forms.Form):
    contract = forms.ModelChoiceField(models.Contract.objects.none())


class EditForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('state', 'year', 'contract_number', 'valid_from', 'valid_to',
                  'contract_file', 'open_source', 'in_communication')


class EmailForm(forms.ModelForm):
    class Meta:
        model = models.EmailNegotiation
        fields = ('scheduled_date', 'title', 'content')
