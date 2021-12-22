from django import forms
from django.utils.translation import ugettext_lazy as _

from . import models, constants
from dal import autocomplete
from contracts.constants import OPEN_SOURCES_TYPES

LICENSE_TYPES = (('', '---'),) + OPEN_SOURCES_TYPES


class SourceForm(forms.ModelForm):
    """
    Adds new source
    """
    main_url = forms.URLField(label=_('Main URL'))

    class Meta:
        model = models.Source
        fields = (
            'name', 'main_url', 'publisher', 'category',
            'keywords', 'suggested_by'
        )

        widgets = {
            'publisher': autocomplete.ModelSelect2(
                url='publishers:autocomplete'
            ),
            'keywords': autocomplete.ModelSelect2Multiple(url='source:keyword_autocomplete'),
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
    def clean(self):
        cleaned_data = super().clean()

        state = cleaned_data.get("state")
        frequency = cleaned_data.get("frequency")
        if (state in constants.ARCHIVING_STATES and
                frequency is None):
            error = forms.ValidationError(
                _("Zdroje se stavem 'Archivován' a 'Archivován bez smlouvy'"
                    " musí mít vybranou Frekvenci sklízení"),
                code="archiving_no_frequency"
            )
            self.add_error("state", error)
            self.add_error("frequency", error)

        return cleaned_data

    class Meta:
        model = models.Source
        fields = ('owner', 'name', 'publisher', 'publisher_contact', 'state',
                  'frequency', 'keywords', 'category', 'sub_category', 'annotation',
                  'screenshot', 'comment', 'aleph_id', 'issn', 'dead_source')

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
            ),
            'keywords': autocomplete.ModelSelect2Multiple(url='source:keyword_autocomplete'),
        }


class SeedEdit(forms.ModelForm):
    class Meta:
        model = models.Seed
        exclude = ['source', 'active']
