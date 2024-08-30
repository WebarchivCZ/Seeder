from captcha.fields import ReCaptchaField
from django import forms
from django.utils.translation import gettext as _

from dal import autocomplete
from . import models
from core.models import SiteConfiguration


class BigSearchForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={'size': '32', 'class': 'query'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If wayback maintenance is on, disable the search box
        maintenance = SiteConfiguration.get_solo().wayback_maintenance or False
        self.fields["query"].disabled = maintenance
        if maintenance:
            self.fields["query"].widget.attrs["placeholder"] = _(
                "Nelze nyní vyhledávat...")


class NewsForm(forms.ModelForm):
    class Meta:
        model = models.NewsObject

        # exclude translated fields
        exclude = [
            'active', 'title', 'annotation',
            'annotation_source_1', 'annotation_source_2'
        ]

        widgets = {
            'source_1': autocomplete.ModelSelect2(
                url='source:source_public_autocomplete'
            ),
            'source_2': autocomplete.ModelSelect2(
                url='source:source_public_autocomplete'
            )
        }


class NominationForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = models.Nomination
        exclude = ['resolved', 'active']

        widgets = {
            'url': forms.Textarea(attrs={'cols': 40, 'rows': 1}),
            'contact_email': forms.Textarea(attrs={'cols': 40, 'rows': 1}),
            'name': forms.Textarea(attrs={'cols': 40, 'rows': 1}),
            'note': forms.Textarea(attrs={'cols': 40, 'rows': 2}),
        }
