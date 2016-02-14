from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


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
        return super(DeletableModelForm, self).save()
