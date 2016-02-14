from django import forms

from core.forms import DeletableModelForm
from . import models


class AddForm(forms.ModelForm):
    class Meta:
        model = models.Blacklist
        fields = ['blacklist_type', 'url_list']


class EditForm(DeletableModelForm):
    class Meta:
        model = models.Blacklist
        fields = ['blacklist_type', 'url_list']
