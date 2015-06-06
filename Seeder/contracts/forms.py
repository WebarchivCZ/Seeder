import models

from django import forms


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('contract_type', )


class EditForm(forms.ModelForm):
    class Meta:
        model = models.Contract
        fields = ('state', 'valid_from', 'valid_to', 'contract_file',
                  'contract_type', 'in_communication')


class EmailForm(forms.ModelForm):
    class Meta:
        model = models.EmailNegotiation
        fields = ('scheduled_date', 'title', 'content')