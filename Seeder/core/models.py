from django.db import models
from django import forms
from django.utils import timezone
from django.forms.widgets import DateTimeInput, SplitDateTimeWidget

from core import widgets


class DatePickerField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': widgets.DatePickerWidget()
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)


class DateTimePickerFormField(forms.DateTimeField):
    """ HTML datetime-local only supports this format """
    input_formats = forms.DateTimeField.input_formats + ['%Y-%m-%dT%H:%M']


class DateTimePickerField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {
            # Need to overwrite te widget as well as the form field
            'widget': widgets.DateTimePickerWidget(format='%Y-%m-%dT%H:%M'),
            'form_class': DateTimePickerFormField,
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)


class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now, editable=False)
    last_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('-last_changed', )
