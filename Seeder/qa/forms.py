from django import forms

from . import models


class QACreateForm(forms.ModelForm):
    class Meta:
        model = models.QualityAssuranceCheck
        fields = [
            'content_changed',
            'technical_quality_changed',
            'comment'
        ]

class QAEditForm(forms.ModelForm):
    class Meta:
        model = models.QualityAssuranceCheck
        fields = [
            'content_changed',
            'technical_quality_changed',
            'source_action',
            'comment'
        ]
