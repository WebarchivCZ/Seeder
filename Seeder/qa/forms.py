from django import forms

from . import models


class QAForm(forms.ModelForm):
    class Meta:
        model = models.QualityAssuranceCheck
        fields = [
            'content_changed',
            'technical_quality_changed',
            'comment'
        ]
