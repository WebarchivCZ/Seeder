from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from .json_constants import load_constants


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class DeletableModelForm(forms.ModelForm):
    """
    Model form that allows you to delete the object
    """
    delete = forms.BooleanField(
        initial=False,
        required=False,
        help_text=_('Check this to delete this object')
    )

    def save(self, commit=True):
        if self.cleaned_data['delete']:
            return self.instance.delete()
        return super().save()


class UpdateJsonConstantsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically create a field for each available constant
        for key, value in load_constants().items():
            self.fields[key] = forms.CharField(
                max_length=128, required=True, label=key, initial=value,
            )
