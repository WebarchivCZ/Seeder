from django import forms

from core.forms import DeletableModelForm
from . import models


class AddForm(forms.ModelForm):
    class Meta:
        model = models.Blacklist
        fields = ['title', 'blacklist_type', 'url_list']


class EditForm(DeletableModelForm):
    comment = forms.CharField(required=False)

    class Meta:
        model = models.Blacklist
        fields = ['title', 'blacklist_type', 'url_list', 'comment']
