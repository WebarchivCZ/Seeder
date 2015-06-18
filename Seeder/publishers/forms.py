import models

from django import forms
from django.utils.translation import ugettext as _


class PublisherForm(forms.ModelForm):
    """
        Form that creates new publisher along with new contact person
    """
    contact_name = forms.CharField(
        required=False,
        max_length=64,
        help_text='Name of the contact person')
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)

    class Meta:
        model = models.Publisher
        fields = ('name', 'website')

    def save(self, commit=True):
        """
        Saves new publisher and the new contact

        !Returns tuple of new objects!
        """
        publisher = super(PublisherForm, self).save()
        if self.cleaned_data['contact_name']:
            new_contact = models.ContactPerson(
                name=self.cleaned_data['contact_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],
                publisher=publisher)
            new_contact.save()
        else:
            new_contact = None
        return publisher, new_contact


class PublisherEditForm(forms.ModelForm):
    class Meta:
        model = models.Publisher
        fields = ('name', 'website')


class ContactChoiceForm(forms.ModelForm):
    """
    Form that lets users choose or create new contact
    """
    # we have to set required=false to these fields
    name = forms.CharField(max_length=64, required=False)
    email = forms.EmailField(required=False)
    contact = forms.ModelChoiceField(
        queryset=models.ContactPerson.objects.all(), required=False)

    def clean(self):
        fields = [self.cleaned_data['contact'], self.cleaned_data['name']]
        if all(fields):
            raise forms.ValidationError(
                _("You can't use old contact and create new at the same time"))
        if self.cleaned_data['name'] and not self.cleaned_data['email']:
            self.add_error('email', _('Please fill-out the email'))

    class Meta:
        model = models.ContactPerson
        fields = ('contact', 'name', 'email', 'phone')


class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = models.ContactPerson
        fields = ('name', 'email', 'phone')
