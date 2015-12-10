from django import forms
from django.utils.translation import ugettext_lazy as _


class PostponeForm(forms.Form):
    postpone_months = forms.IntegerField(
        label=_('Months'),
        help_text=_('type for how many months you wish to postpone this')
    )
