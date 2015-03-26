import models

from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _


class SourceForm(forms.ModelForm):
    new_publisher = forms.CharField(
        required=False,
        help_text=_('Instantly create publisher'))
    
    def __init__(self, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)
        # publisher is not required because user can create
        # new_publisher instantly this could have been done declaratively but
        # then we would loose model level validation etc.
        self.fields['publisher'].required = False
        self.fields['owner'].required = False

    def clean(self):
        cleaned_data = super(SourceForm, self).clean()

        publishers = (cleaned_data['publisher'], cleaned_data['new_publisher'])
        # check that user has either publisher or new_publisher
        if not any(publishers):
            self.add_error('new_publisher', _('Please fill out publisher'))

        if all(publishers):
            self.add_error(
                'new_publisher',
                _('You cannot create a new publisher and use old '
                  'one at the same time!'))

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'publisher', 'new_publisher',
                  'special_contact', 'conspectus', 'sub_conspectus',
                  'web_proposal', 'comment')


SeedFormset = modelformset_factory(models.Seed, fields=('url', ), extra=3)
