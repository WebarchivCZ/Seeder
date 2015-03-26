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

        # curator is also valid field only when user has manage_sources
        # permission
        self.fields['owner'].required = False

    class Meta:
        model = models.Source
        fields = ('name', 'owner', 'publisher', 'new_publisher',
                  'special_contact', 'conspectus', 'sub_conspectus',
                  'web_proposal', 'comment')


SeedFormset = modelformset_factory(models.Seed, fields=('url', ), extra=3)
