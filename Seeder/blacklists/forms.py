from django import forms

from . import models


class AddForm(forms.ModelForm):
    class Meta:
        model = models.Blacklist
        fields = ['blacklist_type', 'url_list']