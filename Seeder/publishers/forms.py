import models

from django import forms


class PublisherForm(forms.ModelForm):
    class Meta:
        model = models.Publisher
        fields = ('name', 'website')


class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = models.ContactPerson
        fields = ('name', 'email', 'phone')
