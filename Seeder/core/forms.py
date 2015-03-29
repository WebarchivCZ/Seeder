import models

from django import forms
from django.forms.models import modelformset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext as _


class SourceForm(forms.ModelForm):
    new_publisher = forms.CharField(
        required=False,
        help_text=_('Instantly create publisher'))


    def clean(self):
        cleaned_data = super(SourceForm, self).clean()

        publishers = (cleaned_data.get('publisher', None),
                      cleaned_data.get('new_publisher', None))
        # check that user has either publisher or new_publisher
        if not any(publishers):
            self.add_error('new_publisher', _('Please fill out publisher'))

        if all(publishers):
            self.add_error(
                'new_publisher',
                _('You cannot create a new publisher and use old '
                  'one at the same time!'))

        return cleaned_data

    class Meta:
        model = models.Source
        fields = ('name', 'publisher', 'new_publisher',
                  'special_contact', 'conspectus', 'sub_conspectus',
                  'web_proposal', 'comment')


class ManagementSourceForm(SourceForm):
    """
    This is pretty much the same as SourceForm with the difference that it
    allows to select owner=curator of the source.
    """
    class Meta:
        model = models.Source
        fields = ('owner', 'name', 'publisher', 'new_publisher',
                  'special_contact', 'conspectus', 'sub_conspectus',
                  'web_proposal', 'comment')


class BaseSeedFormset(BaseFormSet):
    def clean(self):
        """
        Checks that there is always at least one valid seed
        """
        urls = [frm.cleaned_data.get('url', None) for frm in self.forms]
        if not any(urls):
            raise forms.ValidationError(_('There must be at least one seed!'))

SeedFormset = modelformset_factory(
    models.Seed, fields=('url', ), extra=3, formset=BaseSeedFormset)
