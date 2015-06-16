import models

from django import forms
from django.forms.models import modelformset_factory
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _


source_fields = ('name', 'publisher', 'frequency', 'category',
                 'sub_category', 'suggested_by', 'open_license', 'comment')


class SourceForm(forms.ModelForm):
    open_license = forms.BooleanField(
        required=False,
        help_text=_('Is text distributed under open license?')
    )

    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}),
                              required=False)

    class Meta:
        model = models.Source
        fields = source_fields


class ManagementSourceForm(SourceForm):
    """
    This is pretty much the same as SourceForm with the difference that it
    allows to select owner=curator of the source.
    """

    class Meta:
        model = models.Source
        fields = ('owner',) + source_fields


class DuplicityForm(forms.Form):
    """
        This is very simple form that requires user to check that he
        is not creating duplicities.
    """
    unique_record = forms.BooleanField(
        required=True,
        help_text=_('Check if this is really unique source.'))


class BaseSeedFormset(BaseFormSet):
    def clean(self):
        """
        Checks that there is always at least one valid seed
        """
        urls = [frm.cleaned_data.get('url', None) for frm in self.forms]
        valid_urls = filter(None, urls)
        if not valid_urls:
            raise forms.ValidationError(_('There must be at least one seed.'))
        if len(set(valid_urls)) < len(valid_urls):
            raise forms.ValidationError(_('All urls must be unique.'))

SeedFormset = modelformset_factory(models.Seed, fields=('url',), extra=7,
                                   formset=BaseSeedFormset)


class SourceEditForm(forms.ModelForm):
    class Meta:
        model = models.Source
        fields = ('owner', 'name', 'state', 'frequency', 'category',
                  'sub_category', 'comment', 'aleph_id')
