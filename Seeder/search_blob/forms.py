from django import forms


class SearchForm(forms.Form):
	q = forms.CharField()
	# page = forms.IntegerField(min_value=1, blank=True)