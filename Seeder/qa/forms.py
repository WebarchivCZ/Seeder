from django import forms

from . import models


class QAForm(forms.ModelForm):
    class Meta:
        model = models.QualityAssuranceCheck
        exclude = ['active', 'created', 'last_modified']
