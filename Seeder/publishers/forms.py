import models

from django import forms


class PublisherForm(forms.ModelForm):
    """
        Form that creates new publisher along with new contact person
    """
    contact_name = forms.CharField(
        max_length=64,
        help_text='Name of the contact person')
    email = forms.EmailField()
    phone = forms.CharField(required=False)

    class Meta:
        model = models.Publisher
        fields = ('name', 'website')

    def save(self, commit=True):
        publisher = super(PublisherForm, self).save()
        new_contact = models.ContactPerson(
            name=self.cleaned_data['contact_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            publisher=publisher)
        new_contact.save()


class PublisherEditForm(forms.ModelForm):
    class Meta:
        model = models.Publisher
        fields = ('name', 'website')


class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = models.ContactPerson
        fields = ('name', 'email', 'phone')
