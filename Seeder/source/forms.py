import models

from django import forms
from django.utils.translation import ugettext_lazy as _

from dal import autocomplete
from contracts.constants import OPEN_SOURCES_TYPES

LICENSE_TYPES = (('', '---'),) + OPEN_SOURCES_TYPES


class SourceForm(forms.ModelForm):
    open_license = forms.BooleanField(
        required=False,
        help_text=_('Creative commons content')
    )

    class Meta:
        model = models.Source
        fields = ('name', 'publisher', 'category',
                  'suggested_by', 'open_license')

        widgets = {
            'publisher': autocomplete.ModelSelect2(
                    url='publishers:autocomplete'
            )
        }


class ManagementSourceForm(SourceForm):
    """
    This is pretty much the same as SourceForm with the difference that it
    allows to select owner=curator of the source.
    """
    class Meta(SourceForm.Meta):
        fields = ('owner',) + SourceForm.Meta.fields


class DuplicityForm(forms.Form):
    """
        This is very simple form that requires user to check that he
        is not creating duplicities.
    """
    unique_record = forms.BooleanField(
        required=True,
        help_text=_('Check if this is really unique source.'))


class SourceEditForm(forms.ModelForm):
    class Meta:
        model = models.Source
        fields = ('owner', 'name', 'publisher', 'publisher_contact', 'state',
                  'frequency', 'category', 'sub_category', 'annotation',
                  'comment', 'aleph_id', 'issn')

        widgets = {
            'publisher': autocomplete.ModelSelect2(
                    url='publishers:autocomplete'
            ),
            'publisher_contact': autocomplete.ModelSelect2(
                url='publishers:contact_autocomplete',
                forward=['publisher']
            ),
            'category': autocomplete.ModelSelect2(
                url='source:category_autocomplete'
            ),
            'sub_category': autocomplete.ModelSelect2(
                url='source:subcategory_autocomplete',
                forward=['category']
            )
        }
