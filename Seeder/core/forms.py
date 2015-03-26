from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from . import models


class SourceForm(forms.ModelForm):
    new_publisher = forms.CharField(
        help_text=_('Instantly create publisher'))

    class Meta:
        model = models.Source
        fields = ('name', 'owner',  'publisher', 'new_publisher',
                  'special_contact', 'conspectus', 'sub_conspectus',
                  'web_proposal', 'comment')


SeedFormset = modelformset_factory(models.Seed, fields=('url', ), extra=3)
