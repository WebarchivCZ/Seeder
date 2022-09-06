from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from .json_constants import FieldType, load_constants, get_type_for_key


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
            field_type = get_type_for_key(key)
            if field_type == FieldType.BOOL:
                self.fields[key] = forms.BooleanField(
                    label=key, initial=value, required=False)
            elif field_type == FieldType.LONG:
                self.fields[key] = forms.CharField(
                    label=key, initial=value, required=True,
                    widget=forms.Textarea())
            elif field_type == FieldType.RICH:
                self.fields[key] = forms.CharField(
                    label=key, initial=value, required=True,
                    widget=CKEditorWidget(config_name="json_constants"))
            else:  # SHORT
                self.fields[key] = forms.CharField(
                    max_length=128, required=True, label=key, initial=value)
