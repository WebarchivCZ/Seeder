from django import forms


class BigSearchForm(forms.Form):
	query = forms.CharField(
		widget=forms.TextInput(attrs={'size': '32', 'class': 'query'})
	)
