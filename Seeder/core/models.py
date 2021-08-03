from django.db import models
from django.utils import timezone
from django.forms.widgets import DateTimeInput

from core import widgets


class DatePickerField(models.DateField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': widgets.DatePickerWidget()
        }

        defaults.update(kwargs)
        return super().formfield(**defaults)


class DateTimePickerField(models.DateTimeField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': DateTimeInput(format="%d.%m.%Y %H:%M")
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
