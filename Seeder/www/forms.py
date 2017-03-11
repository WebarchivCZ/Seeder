from django import forms
from django import forms

from dal import autocomplete
from . import models


class BigSearchForm(forms.Form):
	query = forms.CharField(
		widget=forms.TextInput(attrs={'size': '32', 'class': 'query'})
	)


class NewsForm(forms.ModelForm):
    class Meta:
        model = models.NewsObject
        
        # exclude translated fields
        exclude = ['active', 'title', 'annotation', 'annotation_source_1', 'annotation_source_2'] 

        widgets = {
            'source_1': autocomplete.ModelSelect2(url='source:source_public_autocomplete'),
            'source_2': autocomplete.ModelSelect2(url='source:source_public_autocomplete')
        }

