import models

from django import forms


class PublisherForm(forms.ModelForm):
    class Meta:
        model = models.Publisher
        fields = ('name', 'website', 'email', 'phone')
